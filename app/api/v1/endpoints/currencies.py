from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    CURRENCY_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate
from app.services.currencies import (
    create_currency,
    delete_currency,
    get_currency,
    list_currencies,
    update_currency,
)

router = APIRouter(prefix="/currencies", tags=["currencies"])

@router.get("/", response_model=list[CurrencyResponse])
async def list_currencies_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["list"])),
):
    return await list_currencies(db, current_user)


@router.post("/", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED)
async def create_currency_endpoint(
    currency_data: CurrencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["create"])),
):
    return await create_currency(db, currency_data, current_user)


@router.get("/{currency_id}", response_model=CurrencyResponse)
async def get_currency_endpoint(
    currency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["read"])),
):
    return await get_currency(db, currency_id, current_user)


@router.put("/{currency_id}", response_model=CurrencyResponse)
async def update_currency_endpoint(
    currency_id: int,
    currency_data: CurrencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["update"])),
):
    return await update_currency(db, currency_id, currency_data, current_user)


@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_currency_endpoint(
    currency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(CURRENCY_PERMISSIONS["delete"])),
):
    await delete_currency(db, currency_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)