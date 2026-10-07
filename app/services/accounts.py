
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


def get_all_accounts(
    db: Session,
    company_id: int,
    type: str | None = None,
    current_user=None,
) -> list[Account]:
    """List all accounts for a company."""
    query = db.query(Account).filter(Account.company_id == company_id)
    if type:
        query = query.filter(Account.type == type)
    return query.all()


def get_account(
    db: Session,
    account_id: int,
    current_user=None,
) -> Account:
    """Get an account by ID."""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise NotFoundError("Account", account_id)
    return account


def create_account(
    db: Session,
    account_data: AccountCreate,
    current_user=None,
) -> Account:
    """Create a new account."""
    account = Account(**account_data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account(
    db: Session,
    account_id: int,
    account_data: AccountUpdate,
    current_user=None,
) -> Account:
    """Update an account."""
    account = get_account(db, account_id, current_user)
    update_data = account_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


def delete_account(
    db: Session,
    account_id: int,
    current_user=None,
) -> None:
    """Soft delete an account."""
    account = get_account(db, account_id, current_user)
    account.is_active = False
    db.commit()
