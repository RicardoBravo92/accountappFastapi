
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.tax import Tax
from app.schemas.tax import TaxCreate, TaxResponse, TaxUpdate

router = APIRouter(prefix="/taxes", tags=["taxes"])


@router.get("/", response_model=list[TaxResponse])
def list_taxes(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_taxes(db, company_id, current_user)


@router.post("/", response_model=TaxResponse, status_code=status.HTTP_201_CREATED)
def create_tax(
    tax_data: TaxCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_tax(db, tax_data, current_user)


@router.get("/{tax_id}", response_model=TaxResponse)
def get_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_tax(db, tax_id, current_user)


@router.put("/{tax_id}", response_model=TaxResponse)
def update_tax(
    tax_id: int,
    tax_data: TaxUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_tax(db, tax_id, tax_data, current_user)


@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_tax(db, tax_id, current_user)


@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_tax(db, tax_id, current_user)
