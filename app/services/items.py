from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def list_items(
    db: Session,
    company_id: int,
    current_user=None,
    category_id: Optional[int] = None,
) -> List[Item]:
    """List items for a company."""
    query = db.query(Item).filter(Item.company_id == company_id)
    if category_id:
        query = query.filter(Item.category_id == category_id)
    return query.all()


def create_item(
    db: Session,
    item_data: ItemCreate,
    current_user=None,
) -> Item:
    """Create a new item."""
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_item(
    db: Session,
    item_id: int,
    current_user=None,
) -> Item:
    """Get an item by ID."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise NotFoundError("Item", item_id)
    return item


def update_item(
    db: Session,
    item_id: int,
    item_data: ItemUpdate,
    current_user=None,
) -> Item:
    """Update an item."""
    item = get_item(db, item_id, current_user)
    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(
    db: Session,
    item_id: int,
    current_user=None,
) -> None:
    """Soft delete an item."""
    item = get_item(db, item_id, current_user)
    item.is_active = False
    db.commit()