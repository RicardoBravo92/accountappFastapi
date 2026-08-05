
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate, TransferResponse, TransferUpdate

router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.get("/", response_model=list[TransferResponse])
def list_transfers(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Transfer)
        .filter(Transfer.company_id == company_id)
        .order_by(Transfer.transferred_at.desc())
        .all()
    )


@router.post("/", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    transfer_data: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transfer = Transfer(**transfer_data.model_dump())
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@router.put("/{transfer_id}", response_model=TransferResponse)
def update_transfer(
    transfer_id: int,
    transfer_data: TransferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    update_data = transfer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transfer, key, value)

    db.commit()
    db.refresh(transfer)
    return transfer


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    db.delete(transfer)
    db.commit()
