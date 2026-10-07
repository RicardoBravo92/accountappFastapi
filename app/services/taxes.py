from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.tax import Tax
from app.schemas.tax import TaxCreate, TaxUpdate


def list_taxes(
    db: Session,
    company_id: int,
    current_user=None,
) -> list[Tax]:
    """List taxes for a company."""
    return db.query(Tax).filter(Tax.company_id == company_id).all()


def create_tax(
    db: Session,
    tax_data: TaxCreate,
    current_user=None,
) -> Tax:
    """Create a new tax."""
    tax = Tax(**tax_data.model_dump())
    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax


def get_tax(
    db: Session,
    tax_id: int,
    current_user=None,
) -> Tax:
    """Get a tax by ID."""
    tax = db.query(Tax).filter(Tax.id == tax_id).first()
    if not tax:
        raise NotFoundError("Tax", tax_id)
    return tax


def update_tax(
    db: Session,
    tax_id: int,
    tax_data: TaxUpdate,
    current_user=None,
) -> Tax:
    """Update a tax."""
    tax = get_tax(db, tax_id, current_user)
    update_data = tax_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tax, key, value)
    db.commit()
    db.refresh(tax)
    return tax


def delete_tax(
    db: Session,
    tax_id: int,
    current_user=None,
) -> None:
    """Soft delete a tax."""
    tax = get_tax(db, tax_id, current_user)
    tax.is_active = False
    db.commit()
