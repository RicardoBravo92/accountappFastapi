
from fastapi import HTTPException

from app.models import Item

async def get_item(db, item_id, current_user) -> Item:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

async def list_items(db, company_id, current_user,category_id=None):
    query = db.query(Item).filter(Item.company_id == company_id,Item.user_id == current_user.id)
    if category_id:
        query = query.filter(Item.category_id == category_id)
    return query.all()

async def create_item(db, item_data, current_user):
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

async def update_item(db, item_id, item_data, current_user):
    item = get_item(db, item_id, current_user)
    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

async def delete_item(db, item_id, current_user):
    item = get_item(db, item_id, current_user)
    item.is_active = False
    db.commit()
    return item