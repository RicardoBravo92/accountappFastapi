
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.auth.user import User
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate


async def get_all_accounts(
        db: Session,
        company_id: int,
        type: str | None = None,
        current_user: User = None,
) -> list[AccountResponse]:
    query = db.query(Account).filter(
        Account.company_id == company_id, Account.user_id == current_user.id
    )
    if type:
        query = query.filter(Account.type == type)
    return query.all()

async def get_account(
    db: Session,
    account_id: int,
    current_user: User = None,
) -> AccountResponse:
    account = db.query(Account).filter(
        Account.id == account_id, Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


async def update_account(
    db: Session,
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = None,
) -> AccountResponse:
    account = get_account(db, account_id, current_user)
    update_data = account_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


async def delete_account(
    db: Session,
    account_id: int,
    current_user: User = None,
) -> None:
    account = get_account(db, account_id, current_user)
    account.is_active = False
    db.commit()


async def create_account(
    db: Session,
    account_data: AccountCreate,
    current_user: User = None,
) -> AccountResponse:
    account = Account(**account_data.model_dump(), user_id=current_user.id)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account
