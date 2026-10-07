from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    ITEM_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.items import (
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemResponse])
async def list_items_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["list"])),
):
    return await list_items(db, current_user)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item_endpoint(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["create"])),
):
    return await create_item(db, item_data, current_user)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["read"])),
):
    return await get_item(db, item_id, current_user)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item_endpoint(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["update"])),
):
    return await update_item(db, item_id, item_data, current_user)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ITEM_PERMISSIONS["delete"])),
):
    await delete_item(db, item_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)