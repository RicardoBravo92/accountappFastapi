"""Tests for company endpoints - mirrors akaunting CompaniesTest.php patterns."""
import pytest

from app.core.auth import hash_password
from app.models.auth.user import User
from app.models.company import Company


@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication tests."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("testpassword123"),
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
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def authenticated_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


class TestCompanyEndpoints:
    """Tests for company CRUD operations."""

    def test_create_company(self, authenticated_client):
        """Test creating a new company."""
        response = authenticated_client.post(
            "/api/v1/companies",
            json={
                "name": "Acme Corp",
                "slug": "acme-corp",
                "email": "info@acme.com",
                "phone": "+1234567890",
                "currency_code": "USD",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Acme Corp"
        assert data["slug"] == "acme-corp"
        assert data["email"] == "info@acme.com"
        assert data["currency_code"] == "USD"
        assert data["is_active"] is True

    def test_get_companies(self, authenticated_client, db_session):
        """Test listing companies."""
        db_session.add(Company(
            name="Test Co 1", slug="test-1", currency_code="USD", is_active=True
        ))
        db_session.add(Company(
            name="Test Co 2", slug="test-2", currency_code="EUR", is_active=True
        ))
        db_session.commit()

        response = authenticated_client.get("/api/v1/companies")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_company_by_id(self, authenticated_client, db_session):
        """Test getting a single company by ID."""
        company = Company(
            name="Single Co", slug="single-co", currency_code="USD", is_active=True
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        response = authenticated_client.get(f"/api/v1/companies/{company.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Single Co"

    def test_get_company_not_found(self, authenticated_client):
        """Test getting a non-existent company returns 404."""
        response = authenticated_client.get("/api/v1/companies/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_company(self, authenticated_client, db_session):
        """Test updating a company."""
        company = Company(
            name="Old Name", slug="old-name", currency_code="USD", is_active=True
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        response = authenticated_client.put(
            f"/api/v1/companies/{company.id}",
            json={"name": "New Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"

    def test_delete_company(self, authenticated_client, db_session):
        """Test soft deleting a company."""
        company = Company(
            name="Delete Co", slug="delete-co", currency_code="USD", is_active=True
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        response = authenticated_client.delete(f"/api/v1/companies/{company.id}")
        assert response.status_code == 204

        # Verify it's soft deleted
        db_session.expire_all()
        updated = db_session.query(Company).filter(Company.id == company.id).first()
        assert updated.is_active is False

    def test_unauthenticated_access_denied(self, client):
        """Test that unauthenticated requests are rejected."""
        response = client.get("/api/v1/companies")
        assert response.status_code == 401
