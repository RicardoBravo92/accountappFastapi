from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyUpdate


def list_currencies(
    db: Session,
    current_user=None,
) -> list[Currency]:
    """List active currencies."""
    return db.query(Currency).filter(Currency.is_active).all()


def create_currency(
    db: Session,
    currency_data: CurrencyCreate,
    current_user=None,
) -> Currency:
    """Create a new currency."""
    currency = Currency(**currency_data.model_dump())
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


def get_currency(
    db: Session,
    currency_id: int,
    current_user=None,
) -> Currency:
    """Get a currency by ID."""
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise NotFoundError("Currency", currency_id)
    return currency


def update_currency(
    db: Session,
    currency_id: int,
    currency_data: CurrencyUpdate,
    current_user=None,
) -> Currency:
    """Update a currency."""
    currency = get_currency(db, currency_id, current_user)
    update_data = currency_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(currency, key, value)
    db.commit()
    db.refresh(currency)
    return currency


def delete_currency(
    db: Session,
    currency_id: int,
    current_user=None,
) -> None:
    """Delete a currency."""
    currency = get_currency(db, currency_id, current_user)
    db.delete(currency)
    db.commit()
