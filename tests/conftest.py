import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_db
from app.core.database import Base
from app.main import app
from app.services.rate_limit import api_rate_limiter, login_rate_limiter

# Try to import testcontainers
try:
    from testcontainers.postgres import PostgresContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False


def _docker_available() -> bool:
    """Check if Docker is available."""
    if not TESTCONTAINERS_AVAILABLE:
        return False
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset rate limiters before each test."""
    api_rate_limiter.reset()
    login_rate_limiter.reset()
    yield
    api_rate_limiter.reset()
    login_rate_limiter.reset()


@pytest.fixture(scope="session")
def test_database():
    """Create a test database - uses PostgreSQL if Docker available, otherwise SQLite."""
    if _docker_available():
        # Use PostgreSQL from testcontainer
        container = PostgresContainer("postgres:16-alpine")
        container.start()
        db_url = container.get_connection_url()
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")

        engine = create_engine(db_url)
        Base.metadata.create_all(bind=engine)

        yield engine

        engine.dispose()
        container.stop()
    else:
        # Fall back to SQLite
        import tempfile
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        db_url = f"sqlite:///{db_path}"

        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
        )

        Base.metadata.create_all(bind=engine)

        yield engine

        engine.dispose()
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except (PermissionError, NameError):
            pass


@pytest.fixture
def db_session(test_database):
    """Create a database session for testing - isolated per test."""
    engine = test_database
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal()
    session.expire_on_commit = False

    # Clear all data before each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    yield session

    # Clean up after test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with the same db_session shared with the API."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
