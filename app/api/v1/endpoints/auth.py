from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.auth import create_access_token, decode_token
from app.models.auth.user import User
from app.schemas.auth import RefreshTokenResponse, UserCreate, UserResponse
from app.services.audit import AuditAction, AuditLogger
from app.services.auth.user_service import (
    authenticate_user,
    create_refresh_token,
    create_user,
    revoke_all_user_tokens,
    revoke_refresh_token,
    verify_and_rotate_refresh_token,
)
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
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    try:
        user = create_user(db, **user_data.model_dump())
        # Audit log
        audit = AuditLogger(db)
        audit.user_create(user.id, request=request)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post(
    "/login",
    response_model=RefreshTokenResponse,
    summary="User login",
    description="Authenticate user with email and password. Returns access token and refresh token for API authentication. Rate limited to 5 attempts per minute per email.",
    response_description="Access token and refresh token with bearer type",
)
def login(
    request: Request,
    username: str = Form(..., description="User email address"),
    password: str = Form(..., description="User password"),
    db: Session = Depends(get_db),
):
    # Check login rate limit before authentication
    check_login_rate_limit(request, username)

    audit = AuditLogger(db)
    user = authenticate_user(db, username, password)
    if not user:
        audit.login_failed(username, request=request, reason="invalid_credentials")
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(db, user.id)

    audit.login_success(user.id, request=request)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


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
    response_model=RefreshTokenResponse,
    summary="Refresh access token with rotation",
    description="Obtain a new access token and refresh token using a valid refresh token. The old refresh token is revoked (rotation).",
    response_description="New access token and refresh token with bearer type",
)
def refresh_token(refresh_token: str = Form(..., description="Refresh token"), db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token with rotation."""
    result = verify_and_rotate_refresh_token(db, refresh_token)
    if not result:
        # Audit failed refresh attempt
        audit = AuditLogger(db)
        # Try to decode to get user_id for audit
        from app.core.auth import decode_token
        payload = decode_token(refresh_token)
        user_id = payload.get("user_id") if payload else None
        audit.log(
            action=AuditAction.TOKEN_REFRESH_FAILED,
            user_id=user_id,
            request=Request,
            status_code=401,
            details={"reason": "invalid_or_expired"},
        )
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Audit successful token refresh
    payload = decode_token(refresh_token)
    user_id = payload.get("user_id") if payload else None
    audit = AuditLogger(db)
    audit.token_refresh(user_id, request=request)

    return result


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and revoke refresh token",
    description="Revoke the current refresh token to logout the user.",
)
def logout(request: Request, refresh_token: str = Form(..., description="Refresh token to revoke"), db: Session = Depends(get_db)):
    """Revoke refresh token on logout."""
    revoke_refresh_token(db, refresh_token)

    # Audit logout
    payload = decode_token(refresh_token)
    user_id = payload.get("user_id") if payload else None
    audit = AuditLogger(db)
    audit.logout(user_id, request=request)

    return None


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout from all devices",
    description="Revoke all refresh tokens for the current user.",
)
def logout_all(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Revoke all refresh tokens for the current user."""
    revoke_all_user_tokens(db, current_user.id)

    # Audit logout all
    audit = AuditLogger(db)
    audit.logout_all(current_user.id, request=request)

    return None
