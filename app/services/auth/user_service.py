
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.auth import hash_password, verify_password
from app.models.auth.user import RefreshToken, User, UserCompany, UserRole


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, **data) -> User:
    user = User(
        email=data["email"],
        username=data["username"],
        password_hash=hash_password(data["password"]),
        first_name=data["first_name"],
        last_name=data["last_name"],
        role=data.get("role", UserRole.VIEWER),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session, company_id: int) -> list[User]:
    """List users belonging to a specific company."""
    return (
        db.query(User)
        .join(User.companies)
        .filter(UserCompany.company_id == company_id)
        .all()
    )


def update_user(db: Session, user_id: int, **data) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


# Refresh Token functions for token rotation

def hash_token(token: str) -> str:
    """Hash a refresh token for storage."""
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(db: Session, user_id: int) -> str:
    """Create a new refresh token and store its hash."""
    from app.core.auth import create_refresh_token as create_jwt_refresh

    # Generate JWT refresh token
    token = create_jwt_refresh(data={"user_id": user_id})

    # Hash for storage
    token_hash = hash_token(token)

    # Calculate expiry
    expires_at = datetime.now(UTC) + timedelta(days=7)  # REFRESH_TOKEN_EXPIRE_DAYS

    # Store in database
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        is_revoked=False,
    )
    db.add(refresh_token)
    db.commit()

    return token


def verify_and_rotate_refresh_token(db: Session, refresh_token: str) -> str | None:
    """Verify a refresh token, revoke it, and issue a new one.

    Returns new access token if successful, None if invalid/expired/revoked.
    """
    from app.core.auth import create_access_token, decode_token

    # Decode JWT to get user_id
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    # Hash the provided token to look up in DB
    token_hash = hash_token(refresh_token)

    # Find the token in database
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.user_id == user_id
    ).first()

    if not stored_token:
        return None

    # Check if revoked
    if stored_token.is_revoked:
        # Possible token reuse attack - revoke all user tokens
        revoke_all_user_tokens(db, user_id)
        return None

    # Check expiry
    if stored_token.expires_at < datetime.now(UTC):
        return None

    # Revoke the old token (rotation)
    stored_token.is_revoked = True
    stored_token.revoked_at = datetime.now(UTC)

    # Create new refresh token
    new_refresh_token = create_refresh_token(db, user_id)

    # Create new access token
    access_token = create_access_token(data={"user_id": user_id})

    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


def revoke_all_user_tokens(db: Session, user_id: int) -> int:
    """Revoke all refresh tokens for a user (e.g., on password change, logout all)."""
    count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        not RefreshToken.is_revoked
    ).update({
        "is_revoked": True,
        "revoked_at": datetime.now(UTC)
    })
    db.commit()
    return count


def revoke_refresh_token(db: Session, refresh_token: str) -> bool:
    """Revoke a specific refresh token (e.g., on logout)."""
    token_hash = hash_token(refresh_token)
    count = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).update({
        "is_revoked": True,
        "revoked_at": datetime.now(UTC)
    })
    db.commit()
    return count > 0


def clean_expired_refresh_tokens(db: Session) -> int:
    """Clean up expired refresh tokens (can be run as a periodic job)."""
    count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(UTC)
    ).delete()
    db.commit()
    return count


user_service = {
    "authenticate_user": authenticate_user,
    "get_user_by_id": get_user_by_id,
    "get_user_by_email": get_user_by_email,
    "create_user": create_user,
    "list_users": list_users,
    "update_user": update_user,
    "delete_user": delete_user,
    "create_refresh_token": create_refresh_token,
    "verify_and_rotate_refresh_token": verify_and_rotate_refresh_token,
    "revoke_all_user_tokens": revoke_all_user_tokens,
    "revoke_refresh_token": revoke_refresh_token,
    "clean_expired_refresh_tokens": clean_expired_refresh_tokens,
}
