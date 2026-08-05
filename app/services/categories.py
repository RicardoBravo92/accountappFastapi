# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.models.auth.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


async def get_all_categories(
    db: Session,
    company_id: int,
    type: str | None = None,
    current_user: User = None,
) -> list[CategoryResponse] | None:
    query = db.query(Category).filter(Category.company_id == company_id)
    if type:
        query = query.filter(Category.type == type)
    return query.all()

async def get_category(
    db: Session,
    category_id: int,
    current_user: User = None,
) -> CategoryResponse | None:
    category = db.query(Category).filter(Category.id == category_id).first()
    return category

async def create_category(
    db: Session,
    category_data: CategoryCreate,
    current_user: User = None,
) -> CategoryResponse | None:
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryResponse(**category.__dict__)

async def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = None,
) -> CategoryResponse | None:
    category = get_category(db, category_id, current_user)
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return CategoryResponse(**category.__dict__)

async def delete_category(
    db: Session,
    category_id: int,
    current_user: User = None,
) -> None:
    category = get_category(db, category_id, current_user)
    category.is_active = False
    db.commit()