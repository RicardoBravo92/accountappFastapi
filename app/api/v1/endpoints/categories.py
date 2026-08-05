from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.categories import category_service

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    company_id: int,
    type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.list_categories(db, company_id, type, current_user)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.create_category(db, category_data, current_user)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.get_category(db, category_id, current_user)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.update_category(db, category_id, category_data, current_user)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.delete_category(db, category_id, current_user)
