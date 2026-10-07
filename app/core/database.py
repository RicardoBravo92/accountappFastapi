from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def get_connect_args(database_url: str) -> dict:
    """Get connection arguments based on database type."""
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {"client_encoding": "utf8"}


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=get_connect_args(settings.DATABASE_URL),
    **settings.get_database_connection_kwargs(),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
