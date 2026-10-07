import pytest

from app.core.auth import hash_password
from app.models.auth.user import User


@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication tests."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user):
    """Get an authentication token for the test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Return authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Return a test client with authentication headers applied."""
    client.headers.update(auth_headers)
    return client


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "password_hash" not in data

    def test_register_user_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "different_user",
                "password": "AnotherPass123!",
                "first_name": "Dup",
                "last_name": "User",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Test successful login returns access token."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPassword123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_me_authenticated(self, authenticated_client):
        """Test getting current user when authenticated."""
        response = authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    def test_get_me_unauthenticated(self, client):
        """Test getting current user without authentication fails."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"] or \
               "Not authenticated" in response.json()["detail"]

    def test_password_is_hashed_on_register(self, client, db_session):
        """Test that password is hashed and not stored in plain text."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "hashcheck@example.com",
                "username": "hashcheck",
                "password": "PlainTextPass123!",
                "first_name": "Hash",
                "last_name": "Check",
            },
        )
        assert response.status_code == 201

        user = db_session.query(User).filter(User.email == "hashcheck@example.com").first()
        assert user is not None
        assert user.password_hash != "PlainTextPass123!"
        assert len(user.password_hash) > 20  # Bcrypt hashes are long
