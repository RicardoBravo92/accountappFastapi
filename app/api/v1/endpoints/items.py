from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.permissions import (
    ITEM_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.items import (
    list_items,
    create_item,
    get_item,
    update_item,
    delete_item,
)

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemResponse])
def list_items_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["list"])),
):
    return list_items(db, current_user)

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item_endpoint(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["create"])),
):
    return create_item(db, item_data, current_user)

@router.get("/{item_id}", response_model=ItemResponse)
def get_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["read"])),
):
    return get_item(db, item_id, current_user)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item_endpoint(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["update"])),
):
    return update_item(db, item_id, item_data, current_user)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["delete"])),
):
    delete_item(db, item_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
