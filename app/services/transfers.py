from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate, TransferUpdate


def list_transfers(
    db: Session,
    company_id: int,
    current_user=None,
) -> list[Transfer]:
    """List transfers for a company."""
    return db.query(Transfer).filter(Transfer.company_id == company_id).order_by(Transfer.transferred_at.desc()).all()


def create_transfer(
    db: Session,
    transfer_data: TransferCreate,
    current_user=None,
) -> Transfer:
    """Create a new transfer."""
    transfer = Transfer(**transfer_data.model_dump())
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


def get_transfer(
    db: Session,
    transfer_id: int,
    current_user=None,
) -> Transfer:
    """Get a transfer by ID."""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise NotFoundError("Transfer", transfer_id)
    return transfer


def update_transfer(
    db: Session,
    transfer_id: int,
    transfer_data: TransferUpdate,
    current_user=None,
) -> Transfer:
    """Update a transfer."""
    transfer = get_transfer(db, transfer_id, current_user)
    update_data = transfer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transfer, key, value)
    db.commit()
    db.refresh(transfer)
    return transfer


def delete_transfer(
    db: Session,
    transfer_id: int,
    current_user=None,
) -> None:
    """Delete a transfer."""
    transfer = get_transfer(db, transfer_id, current_user)
    db.delete(transfer)
    db.commit()
