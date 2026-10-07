from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    TRANSFER_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.transfer import TransferCreate, TransferResponse, TransferUpdate
from app.services.transfers import (
    create_transfer,
    delete_transfer,
    get_transfer,
    list_transfers,
    update_transfer,
)

router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.get("/", response_model=list[TransferResponse])
def list_transfers_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSFER_PERMISSIONS["list"])),
):
    return list_transfers(db, company_id, current_user)

@router.post("/", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer_endpoint(
    transfer_data: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSFER_PERMISSIONS["create"])),
):
    return create_transfer(db, transfer_data, current_user)

@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer_endpoint(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSFER_PERMISSIONS["read"])),
):
    return get_transfer(db, transfer_id, current_user)

@router.put("/{transfer_id}", response_model=TransferResponse)
def update_transfer_endpoint(
    transfer_id: int,
    transfer_data: TransferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSFER_PERMISSIONS["update"])),
):
    return update_transfer(db, transfer_id, transfer_data, current_user)

@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer_endpoint(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TRANSFER_PERMISSIONS["delete"])),
):
    delete_transfer(db, transfer_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
