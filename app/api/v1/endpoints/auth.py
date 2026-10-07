from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import get_current_user, get_db
from app.core.auth import create_access_token, decode_token
from app.models.auth.user import User
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services.auth.user_service import create_user, authenticate_user
from app.services.rate_limit import check_login_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, password, and profile information. Returns the created user object without password hash.",
    response_description="Successfully created user",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, **user_data.model_dump())
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user with email and password. Returns access token for API authentication. Rate limited to 5 attempts per minute per email.",
    response_description="Access token with bearer type",
)
def login(
    request: Request,
    username: str = Form(..., description="User email address"),
    password: str = Form(..., description="User password"),
    db: Session = Depends(get_db),
):
    # Check login rate limit before authentication
    check_login_rate_limit(request, username)
    
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile information. Requires valid access token.",
    response_description="Current user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Obtain a new access token using a valid refresh token. Refresh tokens expire after 7 days.",
    response_description="New access token with bearer type",
)
def refresh_token(refresh_token: str = Form(..., description="Refresh token"), db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
