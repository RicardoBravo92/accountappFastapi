from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from app.services.invoices import invoice_service

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/", response_model=list[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return invoice_service.list_invoices(db, current_user)

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return invoice_service.create_invoice(db, invoice_data, current_user)

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return invoice_service.get_invoice(db, invoice_id, current_user)

@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return invoice_service.update_invoice(db, invoice_id, invoice_data, current_user)

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return invoice_service.delete_invoice(db, invoice_id, current_user)
