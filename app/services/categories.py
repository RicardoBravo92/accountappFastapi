from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(
    db: Session,
    company_id: int,
    type: Optional[str] = None,
    current_user=None,
) -> List[Category]:
    """List categories for a company."""
    query = db.query(Category).filter(Category.company_id == company_id)
    if type:
        query = query.filter(Category.type == type)
    return query.all()


def get_category(
    db: Session,
    category_id: int,
    current_user=None,
) -> Category:
    """Get a category by ID."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundError("Category", category_id)
    return category


def create_category(
    db: Session,
    category_data: CategoryCreate,
    current_user=None,
) -> Category:
    """Create a new category."""
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate,
    current_user=None,
) -> Category:
    """Update a category."""
    category = get_category(db, category_id, current_user)
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(
    db: Session,
    category_id: int,
    current_user=None,
) -> None:
    """Soft delete a category."""
    category = get_category(db, category_id, current_user)
    category.is_active = False
    db.commit()