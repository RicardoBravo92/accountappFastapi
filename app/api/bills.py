from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.auth.user import User
from app.models.bill import Bill, BillStatus
from app.schemas.bill import BillCreate, BillResponse, BillUpdate

router = APIRouter(prefix="/bills", tags=["bills"])


@router.get("/", response_model=list[BillResponse])
def list_bills(
    company_id: int,
    status: Optional[str] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Bill).filter(Bill.company_id == company_id)
    if status:
        query = query.filter(Bill.status == status)
    if vendor_id:
        query = query.filter(Bill.vendor_id == vendor_id)
    return query.order_by(Bill.due_date.desc()).all()


@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = Bill(
        company_id=bill_data.company_id,
        vendor_id=bill_data.vendor_id,
        bill_number=bill_data.bill_number,
        status=BillStatus.DRAFT,
        issue_date=bill_data.issue_date,
        due_date=bill_data.due_date,
        currency_code=bill_data.currency_code,
        notes=bill_data.notes,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    update_data = bill_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bill, key, value)

    db.commit()
    db.refresh(bill)
    return bill


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    db.delete(bill)
    db.commit()