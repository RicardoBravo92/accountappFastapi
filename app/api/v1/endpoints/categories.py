from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    CATEGORY_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.categories import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryResponse])
def list_categories_endpoint(
    company_id: int,
    type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CATEGORY_PERMISSIONS["list"])),
):
    return list_categories(db, company_id, type, current_user)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CATEGORY_PERMISSIONS["create"])),
):
    return create_category(db, category_data, current_user)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CATEGORY_PERMISSIONS["read"])),
):
    return get_category(db, category_id, current_user)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CATEGORY_PERMISSIONS["update"])),
):
    return update_category(db, category_id, category_data, current_user)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CATEGORY_PERMISSIONS["delete"])),
):
    delete_category(db, category_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
