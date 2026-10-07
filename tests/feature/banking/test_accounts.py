"""Tests for account endpoints - mirrors akaunting Banking/AccountsTest.php patterns."""
import pytest

from app.core.auth import hash_password
from app.models.account import Account, AccountType
from app.models.auth.user import User
from app.models.company import Company


@pytest.fixture
def test_user(db_session):
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
def test_company(db_session, test_user):
    company = Company(
        name="Test Company", slug="test-company", currency_code="USD", is_active=True
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def auth_token(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def authenticated_client(client, auth_token):
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client


class TestAccountEndpoints:
    """Tests for account CRUD operations."""

    def test_create_account(self, authenticated_client, test_company):
        """Test creating a new account."""
        response = authenticated_client.post(
            "/api/v1/accounts",
            json={
                "company_id": test_company.id,
                "code": "1000",
                "name": "Cash",
                "type": "asset",
                "is_bank": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "1000"
        assert data["name"] == "Cash"
        assert data["type"] == "asset"
        assert data["is_bank"] is True
        assert data["is_active"] is True
        assert data["company_id"] == test_company.id

    def test_list_accounts(self, authenticated_client, db_session, test_company):
        """Test listing accounts filtered by company."""
        db_session.add(Account(
            company_id=test_company.id, code="1000", name="Cash",
            type=AccountType.ASSET, is_active=True
        ))
        db_session.add(Account(
            company_id=test_company.id, code="2000", name="Bank",
            type=AccountType.ASSET, is_bank=True, is_active=True
        ))
        db_session.commit()

        response = authenticated_client.get(
            f"/api/v1/accounts?company_id={test_company.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_account_by_id(self, authenticated_client, db_session, test_company):
        """Test getting a single account by ID."""
        account = Account(
            company_id=test_company.id, code="1000", name="Cash",
            type=AccountType.ASSET, is_active=True
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        response = authenticated_client.get(f"/api/v1/accounts/{account.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Cash"
        assert data["code"] == "1000"

    def test_get_account_not_found(self, authenticated_client):
        """Test getting a non-existent account returns 404."""
        response = authenticated_client.get("/api/v1/accounts/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_account(self, authenticated_client, db_session, test_company):
        """Test updating an account."""
        account = Account(
            company_id=test_company.id, code="1000", name="Cash",
            type=AccountType.ASSET, is_active=True
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        response = authenticated_client.put(
            f"/api/v1/accounts/{account.id}",
            json={"name": "Petty Cash"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Petty Cash"

    def test_delete_account(self, authenticated_client, db_session, test_company):
        """Test soft deleting an account."""
        account = Account(
            company_id=test_company.id, code="1000", name="Cash",
            type=AccountType.ASSET, is_active=True
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        response = authenticated_client.delete(f"/api/v1/accounts/{account.id}")
        assert response.status_code == 204

        db_session.expire_all()
        updated = db_session.query(Account).filter(Account.id == account.id).first()
        assert updated.is_active is False

    def test_filter_accounts_by_type(self, authenticated_client, db_session, test_company):
        """Test filtering accounts by type."""
        db_session.add(Account(
            company_id=test_company.id, code="1000", name="Cash",
            type=AccountType.ASSET, is_active=True
        ))
        db_session.add(Account(
            company_id=test_company.id, code="4000", name="Revenue",
            type=AccountType.INCOME, is_active=True
        ))
        db_session.commit()

        response = authenticated_client.get(
            f"/api/v1/accounts?company_id={test_company.id}&type=asset"
        )
        assert response.status_code == 200
        data = response.json()
        assert all(a["type"] == "asset" for a in data)
