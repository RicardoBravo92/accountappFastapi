
from sqlalchemy.orm import Session

from app.core.auth import hash_password, verify_password
from app.models.auth.user import User, UserRole


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
    return db.query(User).all()


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
