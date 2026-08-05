from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate, TransferResponse, TransferUpdate
from app.services.transfers import transfer_service

router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.get("/", response_model=list[TransferResponse])
async def list_transfers(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await transfer_service["list_transfers"](db, company_id, current_user)

@router.post("/", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer_data: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await transfer_service["create_transfer"](db, transfer_data, current_user)

@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await transfer_service["get_transfer"](db, transfer_id, current_user)

@router.put("/{transfer_id}", response_model=TransferResponse)
async def update_transfer(
    transfer_id: int,
    transfer_data: TransferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await transfer_service["update_transfer"](db, transfer_id, transfer_data, current_user)

@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await transfer_service["delete_transfer"](db, transfer_id, current_user)
