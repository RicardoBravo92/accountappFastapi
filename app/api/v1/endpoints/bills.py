from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    BILL_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.services.bills import (
    create_bill,
    delete_bill,
    get_all_bills,
    get_bill,
    update_bill,
)

router = APIRouter(prefix="/bills", tags=["bills"])

@router.get("/", response_model=list[BillResponse])
async def list_bills_endpoint(
    company_id: int,
    status: str | None = None,
    vendor_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["list"])),
):
    return await get_all_bills(db, company_id, status, vendor_id, current_user)


@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill_endpoint(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["create"])),
):
    return await create_bill(db, bill_data, current_user)


@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill_endpoint(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["read"])),
):
    return await get_bill(db, bill_id, current_user)


@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill_endpoint(
    bill_id: int,
    bill_data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["update"])),
):
    return await update_bill(db, bill_id, bill_data, current_user)


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill_endpoint(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(BILL_PERMISSIONS["delete"])),
):
    await delete_bill(db, bill_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)