from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.bill import Bill, BillStatus
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.services.bills import bills_service

router = APIRouter(prefix="/bills", tags=["bills"])

@router.get("/", response_model=list[BillResponse])
async def list_bills(
    company_id: int,
    status: str | None = None,
    vendor_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await bills_service["get_all_bills"](db, company_id, status, vendor_id, current_user)

@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await bills_service["create_bill"](db, bill_data, current_user)

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await bills_service["get_bill"](db, bill_id, current_user)

@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: int,
    bill_data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await bills_service["update_bill"](db, bill_id, bill_data, current_user)

@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await bills_service["delete_bill"](db, bill_id, current_user)
