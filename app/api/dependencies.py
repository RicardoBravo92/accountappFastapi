
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.auth import decode_token
from app.database import SessionLocal
from app.models.auth.user import User

security = HTTPBearer(auto_error=False)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AuthenticationError(Exception):
    """Base exception for authentication-related errors."""

    pass


class TokenError(AuthenticationError):
    """Exception raised for token validation errors."""

    pass


class UserNotFoundError(AuthenticationError):
    """Exception raised when user is not found."""

    pass


class UserInactiveError(AuthenticationError):
    """Exception raised when user account is inactive."""

    pass


def validate_token(token: str) -> dict:
    """Validate JWT token and return payload.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Token payload
        
    Raises:
        TokenError: If token is invalid or expired
    """
    payload = decode_token(token)
    if not payload:
        raise TokenError("Invalid token")

    if "user_id" not in payload:
        raise TokenError("Invalid token payload")
    if payload.get("type") != "access":
        raise TokenError("Invalid token type")

    return payload


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get authenticated user from token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: For authentication failures
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        token = credentials.credentials
        payload = validate_token(token)

        user_id = payload["user_id"]
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        if not user.is_active:
            raise UserInactiveError(f"User {user.username} is inactive")

        return user

    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Token validation error: {str(e)}"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current user for API endpoints.
    
    This is the main dependency function used by API endpoints.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
    """
    return get_authenticated_user(credentials, db)
