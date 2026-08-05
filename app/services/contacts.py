from fastapi import HTTPException

from app.models.contact import Contact


async def list_contacts(db, company_id, type=None, current_user=None):
    query = db.query(Contact).filter(Contact.company_id == company_id)
    if type:
        query = query.filter(Contact.type == type)
    return query.all()


async def create_contact(db, contact_data, current_user):
    contact = Contact(**contact_data.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def get_contact(db, contact_id, current_user):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


async def update_contact(db, contact_id, contact_data, current_user):
    contact = get_contact(db, contact_id, current_user)
    update_data = contact_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


async def delete_contact(db, contact_id, current_user):
    contact = get_contact(db, contact_id, current_user)
    db.delete(contact)
    db.commit()
    return contact


contact_service = {
    "list_contacts": list_contacts,
    "create_contact": create_contact,
    "get_contact": get_contact,
    "update_contact": update_contact,
    "delete_contact": delete_contact,
}
