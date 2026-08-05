from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyResponse, CurrencyUpdate
from app.services.currencies import currency_service

router = APIRouter(prefix="/currencies", tags=["currencies"])

@router.get("/", response_model=list[CurrencyResponse])
def list_currencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return currency_service.list_currencies(db, current_user)

@router.post("/", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED)
def create_currency(
    currency_data: CurrencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return currency_service.create_currency(db, currency_data, current_user)

@router.get("/{currency_id}", response_model=CurrencyResponse)
def get_currency(
    currency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return currency_service.get_currency(db, currency_id, current_user)

@router.put("/{currency_id}", response_model=CurrencyResponse)
def update_currency(
    currency_id: int,
    currency_data: CurrencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return currency_service.update_currency(db, currency_id, currency_data, current_user)

@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_currency(
    currency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return currency_service.delete_currency(db, currency_id, current_user)
