from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
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
    return db.query(Tax).filter(Tax.company_id == company_id).all()


@router.post("/", response_model=TaxResponse, status_code=status.HTTP_201_CREATED)
def create_tax(
    tax_data: TaxCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tax = Tax(**tax_data.model_dump())
    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax


@router.get("/{tax_id}", response_model=TaxResponse)
def get_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tax = db.query(Tax).filter(Tax.id == tax_id).first()
    if not tax:
        raise HTTPException(status_code=404, detail="Tax not found")
    return tax


@router.put("/{tax_id}", response_model=TaxResponse)
def update_tax(
    tax_id: int,
    tax_data: TaxUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tax = db.query(Tax).filter(Tax.id == tax_id).first()
    if not tax:
        raise HTTPException(status_code=404, detail="Tax not found")

    update_data = tax_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tax, key, value)

    db.commit()
    db.refresh(tax)
    return tax


@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tax = db.query(Tax).filter(Tax.id == tax_id).first()
    if not tax:
        raise HTTPException(status_code=404, detail="Tax not found")
    tax.is_active = False
    db.commit()