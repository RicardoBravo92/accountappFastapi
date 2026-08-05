from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.items import item_service

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemResponse])
def list_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return item_service.list_items(db, current_user)

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return item_service.create_item(db, item_data, current_user)

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return item_service.get_item(db, item_id, current_user)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return item_service.update_item(db, item_id, item_data, current_user)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return item_service.delete_item(db, item_id, current_user)
