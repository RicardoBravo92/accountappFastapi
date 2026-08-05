"""Tests for contact endpoints - mirrors akaunting CustomersTest.php and VendorsTest.php patterns."""
import pytest

from app.core.auth import hash_password
from app.models.auth.user import User
from app.models.company import Company
from app.models.contact import Contact


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


class TestContactEndpoints:
    """Tests for contact CRUD operations - mirrors akaunting CustomersTest.php."""

    def test_create_customer_contact(self, authenticated_client, test_company):
        """Test creating a customer contact."""
        response = authenticated_client.post(
            "/api/v1/contacts",
            json={
                "company_id": test_company.id,
                "type": "customer",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["type"] == "customer"
        assert data["email"] == "john@example.com"
        assert data["company_id"] == test_company.id

    def test_create_vendor_contact(self, authenticated_client, test_company):
        """Test creating a vendor contact."""
        response = authenticated_client.post(
            "/api/v1/contacts",
            json={
                "company_id": test_company.id,
                "type": "vendor",
                "name": "Acme Supply Co",
                "email": "supplier@acme.com",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "vendor"

    def test_list_contacts(self, authenticated_client, db_session, test_company):
        """Test listing contacts for a company."""
        db_session.add(Contact(
            company_id=test_company.id, type="customer", name="Customer 1", is_active=True
        ))
        db_session.add(Contact(
            company_id=test_company.id, type="vendor", name="Vendor 1", is_active=True
        ))
        db_session.commit()

        response = authenticated_client.get(
            f"/api/v1/contacts?company_id={test_company.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_list_contacts_with_type_filter(self, authenticated_client, db_session, test_company):
        """Test filtering contacts by type."""
        db_session.add(Contact(
            company_id=test_company.id, type="customer", name="Customer 1", is_active=True
        ))
        db_session.add(Contact(
            company_id=test_company.id, type="vendor", name="Vendor 1", is_active=True
        ))
        db_session.commit()

        response = authenticated_client.get(
            f"/api/v1/contacts?company_id={test_company.id}&type=customer"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "customer"

    def test_get_contact_by_id(self, authenticated_client, db_session, test_company):
        """Test getting a single contact by ID."""
        contact = Contact(
            company_id=test_company.id, type="customer",
            name="Single Contact", email="single@example.com", is_active=True
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        response = authenticated_client.get(f"/api/v1/contacts/{contact.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Single Contact"

    def test_update_contact(self, authenticated_client, db_session, test_company):
        """Test updating a contact."""
        contact = Contact(
            company_id=test_company.id, type="customer",
            name="Old Name", is_active=True
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        response = authenticated_client.put(
            f"/api/v1/contacts/{contact.id}",
            json={"name": "Updated Name", "email": "new@email.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "new@email.com"

    def test_delete_contact(self, authenticated_client, db_session, test_company):
        """Test soft deleting a contact."""
        contact = Contact(
            company_id=test_company.id, type="customer", name="Delete Me", is_active=True
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        response = authenticated_client.delete(f"/api/v1/contacts/{contact.id}")
        assert response.status_code == 204

        db_session.expire_all()
        updated = db_session.query(Contact).filter(Contact.id == contact.id).first()
        assert updated.is_active is False

    def test_unauthenticated_access_denied(self, client, test_company):
        """Test that unauthenticated requests are rejected for contacts."""
        response = client.get(f"/api/v1/contacts?company_id={test_company.id}")
        assert response.status_code == 401