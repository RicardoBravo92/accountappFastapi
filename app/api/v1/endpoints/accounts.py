from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    ACCOUNT_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.services.accounts import (
    create_account,
    delete_account,
    get_account,
    get_all_accounts,
    update_account,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/", response_model=list[AccountResponse])
def list_accounts_endpoint(
    company_id: int,
    type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ACCOUNT_PERMISSIONS["list"])),
):
    return get_all_accounts(db, company_id, type, current_user)

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account_endpoint(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ACCOUNT_PERMISSIONS["create"])),
):
    return create_account(db, account_data, current_user)

@router.get("/{account_id}", response_model=AccountResponse)
def get_account_endpoint(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ACCOUNT_PERMISSIONS["read"])),
):
    return get_account(db, account_id, current_user)

@router.put("/{account_id}", response_model=AccountResponse)
def update_account_endpoint(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ACCOUNT_PERMISSIONS["update"])),
):
    return update_account(db, account_id, account_data, current_user)

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account_endpoint(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ACCOUNT_PERMISSIONS["delete"])),
):
    delete_account(db, account_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
