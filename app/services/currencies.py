from fastapi import HTTPException

from app.models.currency import Currency


async def list_currencies(db, current_user):
    return db.query(Currency).filter(Currency.is_active == True).all()


async def create_currency(db, currency_data, current_user):
    currency = Currency(**currency_data.model_dump())
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


async def get_currency(db, currency_id, current_user):
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency


async def update_currency(db, currency_id, currency_data, current_user):
    currency = get_currency(db, currency_id, current_user)
    update_data = currency_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(currency, key, value)
    db.commit()
    db.refresh(currency)
    return currency


async def delete_currency(db, currency_id, current_user):
    currency = get_currency(db, currency_id, current_user)
    db.delete(currency)
    db.commit()
    return currency


currency_service = {
    "list_currencies": list_currencies,
    "create_currency": create_currency,
    "get_currency": get_currency,
    "update_currency": update_currency,
    "delete_currency": delete_currency,
}
