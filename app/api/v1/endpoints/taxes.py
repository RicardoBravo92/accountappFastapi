from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    TAX_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.tax import TaxCreate, TaxResponse, TaxUpdate
from app.services.taxes import (
    create_tax,
    delete_tax,
    get_tax,
    list_taxes,
    update_tax,
)

router = APIRouter(prefix="/taxes", tags=["taxes"])

@router.get("/", response_model=list[TaxResponse])
def list_taxes_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TAX_PERMISSIONS["list"])),
):
    return list_taxes(db, current_user)

@router.post("/", response_model=TaxResponse, status_code=status.HTTP_201_CREATED)
def create_tax_endpoint(
    tax_data: TaxCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TAX_PERMISSIONS["create"])),
):
    return create_tax(db, tax_data, current_user)

@router.get("/{tax_id}", response_model=TaxResponse)
def get_tax_endpoint(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TAX_PERMISSIONS["read"])),
):
    return get_tax(db, tax_id, current_user)

@router.put("/{tax_id}", response_model=TaxResponse)
def update_tax_endpoint(
    tax_id: int,
    tax_data: TaxUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TAX_PERMISSIONS["update"])),
):
    return update_tax(db, tax_id, tax_data, current_user)

@router.delete("/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tax_endpoint(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(TAX_PERMISSIONS["delete"])),
):
    delete_tax(db, tax_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
