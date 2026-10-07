from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    TRANSACTION_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.transactions import (
    create_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=list[TransactionResponse])
def list_transactions_endpoint(
    company_id: int,
    account_id: int | None = None,
    type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSACTION_PERMISSIONS["list"])),
):
    return list_transactions(db, company_id, account_id, type, current_user)

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction_endpoint(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSACTION_PERMISSIONS["create"])),
):
    return create_transaction(db, transaction_data, current_user)

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_endpoint(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSACTION_PERMISSIONS["read"])),
):
    return get_transaction(db, transaction_id, current_user)

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction_endpoint(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSACTION_PERMISSIONS["update"])),
):
    return update_transaction(db, transaction_id, transaction_data, current_user)

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction_endpoint(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSACTION_PERMISSIONS["delete"])),
):
    delete_transaction(db, transaction_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
