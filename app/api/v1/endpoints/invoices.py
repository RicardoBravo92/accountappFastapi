from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    INVOICE_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from app.services.invoices import (
    create_invoice,
    delete_invoice,
    get_invoice,
    list_invoices,
    update_invoice,
)

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(INVOICE_PERMISSIONS["list"])),
):
    return await list_invoices(db, current_user)


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice_endpoint(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(INVOICE_PERMISSIONS["create"])),
):
    return await create_invoice(db, invoice_data, current_user)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(INVOICE_PERMISSIONS["read"])),
):
    return await get_invoice(db, invoice_id, current_user)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice_endpoint(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(INVOICE_PERMISSIONS["update"])),
):
    return await update_invoice(db, invoice_id, invoice_data, current_user)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(INVOICE_PERMISSIONS["delete"])),
):
    await delete_invoice(db, invoice_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)