from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.permissions import (
    BILL_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.services.bills import (
    get_all_bills,
    create_bill,
    get_bill,
    update_bill,
    delete_bill,
)

router = APIRouter(prefix="/bills", tags=["bills"])

@router.get("/", response_model=list[BillResponse])
def list_bills_endpoint(
    company_id: int,
    status: str | None = None,
    vendor_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["list"])),
):
    return get_all_bills(db, company_id, status, vendor_id, current_user)

@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill_endpoint(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["create"])),
):
    return create_bill(db, bill_data, current_user)

@router.get("/{bill_id}", response_model=BillResponse)
def get_bill_endpoint(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["read"])),
):
    return get_bill(db, bill_id, current_user)

@router.put("/{bill_id}", response_model=BillResponse)
def update_bill_endpoint(
    bill_id: int,
    bill_data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["update"])),
):
    return update_bill(db, bill_id, bill_data, current_user)

@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill_endpoint(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["delete"])),
):
    delete_bill(db, bill_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
