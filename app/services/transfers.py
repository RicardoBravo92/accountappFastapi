from fastapi import HTTPException
from app.models.transfer import Transfer

async def list_transfers(db, company_id, current_user=None):
    return db.query(Transfer).filter(Transfer.company_id == company_id).order_by(Transfer.transferred_at.desc()).all()

async def create_transfer(db, transfer_data, current_user):
    transfer = Transfer(**transfer_data.model_dump())
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer

async def get_transfer(db, transfer_id, current_user=None):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer

async def update_transfer(db, transfer_id, transfer_data, current_user=None):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    update_data = transfer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transfer, key, value)
    db.commit()
    db.refresh(transfer)
    return transfer

async def delete_transfer(db, transfer_id, current_user=None):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    db.delete(transfer)
    db.commit()
    