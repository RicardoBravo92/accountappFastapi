from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


def list_contacts(
    db: Session,
    company_id: int,
    type: Optional[str] = None,
    current_user=None,
) -> List[Contact]:
    """List contacts for a company."""
    query = db.query(Contact).filter(Contact.company_id == company_id)
    if type:
        query = query.filter(Contact.type == type)
    return query.all()


def create_contact(
    db: Session,
    contact_data: ContactCreate,
    current_user=None,
) -> Contact:
    """Create a new contact."""
    contact = Contact(**contact_data.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def get_contact(
    db: Session,
    contact_id: int,
    current_user=None,
) -> Contact:
    """Get a contact by ID."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise NotFoundError("Contact", contact_id)
    return contact


def update_contact(
    db: Session,
    contact_id: int,
    contact_data: ContactUpdate,
    current_user=None,
) -> Contact:
    """Update a contact."""
    contact = get_contact(db, contact_id, current_user)
    update_data = contact_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(
    db: Session,
    contact_id: int,
    current_user=None,
) -> Contact:
    """Soft delete a contact."""
    contact = get_contact(db, contact_id, current_user)
    contact.is_active = False
    db.commit()
    return contact