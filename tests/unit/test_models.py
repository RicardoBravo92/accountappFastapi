import pytest
from datetime import datetime
from app.models.auth.user import User, UserRole
from app.models.company import Company
from app.models.contact import Contact
from app.models.account import Account, AccountType
from app.models.transaction import Transaction, TransactionType


def test_user_creation():
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        role=UserRole.VIEWER
    )
    
    assert user.id is None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.role == UserRole.VIEWER
    assert user.is_active is True
    assert user.created_at is not None


def test_company_creation():
    company = Company(
        name="Test Company",
        slug="test-company",
        email="contact@test.com",
        phone="1234567890"
    )
    
    assert company.id is None
    assert company.name == "Test Company"
    assert company.slug == "test-company"
    assert company.email == "contact@test.com"
    assert company.currency_code == "USD"
    assert company.is_active is True


def test_account_creation():
    account = Account(
        code="1000",
        name="Cash",
        type=AccountType.ASSET,
        is_bank=True
    )
    
    assert account.id is None
    assert account.code == "1000"
    assert account.name == "Cash"
    assert account.type == AccountType.ASSET
    assert account.is_bank is True
    assert account.is_active is True


def test_transaction_creation():
    transaction = Transaction(
        type=TransactionType.DEPOSIT,
        amount=100.50,
        currency_code="USD",
        description="Test transaction",
        reference="REF123"
    )
    
    assert transaction.id is None
    assert transaction.type == TransactionType.DEPOSIT
    assert transaction.amount == 100.50
    assert transaction.currency_code == "USD"
    assert transaction.description == "Test transaction"
    assert transaction.reference == "REF123"
    assert transaction.is_reconciled is False