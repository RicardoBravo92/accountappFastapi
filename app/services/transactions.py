from fastapi import HTTPException

from app.models.transaction import Transaction


async def list_transactions(db, company_id, account_id=None, type=None, current_user=None):
    query = db.query(Transaction).filter(Transaction.company_id == company_id)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if type:
        query = query.filter(Transaction.type == type)
    return query.order_by(Transaction.transferred_at.desc()).all()

async def create_transaction(db, transaction_data, current_user):
    transaction = Transaction(**transaction_data.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

async def get_transaction(db, transaction_id, current_user):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

async def update_transaction(db, transaction_id, transaction_data, current_user):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = transaction_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction

async def delete_transaction(db, transaction_id, current_user):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()


transaction_service = {
    "list_transactions": list_transactions,
    "create_transaction": create_transaction,
    "get_transaction": get_transaction,
    "update_transaction": update_transaction,
    "delete_transaction": delete_transaction,
}
