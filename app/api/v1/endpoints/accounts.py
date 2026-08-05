from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.services.accounts import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/", response_model=list[AccountResponse])
def list_accounts(
    company_id: int,
    type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.get_all_accounts(db, company_id, type, current_user)

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.create_account(db, account_data, current_user)

@router.get("/{account_id}", response_model=AccountResponse)
def read_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.get_account(db, account_id, current_user)

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.update_account(db, account_id, account_data, current_user)

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.delete_account(db, account_id, current_user)
