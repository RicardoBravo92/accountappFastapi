
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth.user import User
from app.repositories.base_repository import BaseRepository
from app.schemas.auth.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User-specific repository extending BaseRepository."""

    def get_by_email(self, db: Session, email: str) -> User | None:
        """Get user by email address."""
        return db.execute(
            select(User).where(User.email == email)
        ).scalars().first()

    def get_by_username(self, db: Session, username: str) -> User | None:
        """Get user by username."""
        return db.execute(
            select(User).where(User.username == username)
        ).scalars().first()

    def is_active(self, db: Session, user_id: int) -> bool:
        """Check if user is active."""
        user = self.get(db, user_id)
        return user.is_active if user else False


user_repository = UserRepository(User)
