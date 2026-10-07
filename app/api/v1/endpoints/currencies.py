from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.permissions import (
    CURRENCY_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate
from app.services.currencies import (
    list_currencies,
    create_currency,
    get_currency,
    update_currency,
    delete_currency,
)

router = APIRouter(prefix="/currencies", tags=["currencies"])

@router.get("/", response_model=list[CurrencyResponse])
def list_currencies_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["list"])),
):
    return list_currencies(db, current_user)

@router.post("/", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED)
def create_currency_endpoint(
    currency_data: CurrencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["create"])),
):
    return create_currency(db, currency_data, current_user)

@router.get("/{currency_id}", response_model=CurrencyResponse)
def get_currency_endpoint(
    currency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["read"])),
):
    return get_currency(db, currency_id, current_user)

@router.put("/{currency_id}", response_model=CurrencyResponse)
def update_currency_endpoint(
    currency_id: int,
    currency_data: CurrencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["update"])),
):
    return update_currency(db, currency_id, currency_data, current_user)

@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_currency_endpoint(
    currency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["delete"])),
):
    delete_currency(db, currency_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
