
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.bill import Bill, BillStatus
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.services.bills import get_all_bills ,get_bill,update_bill,delete_bill,create_bill

router = APIRouter(prefix="/bills", tags=["bills"])


@router.get("/", response_model=list[BillResponse])
def list_bills(
    company_id: int,
    status: str | None = None,
    vendor_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_bills(
        db,
        company_id,
        status,
        vendor_id,
        current_user,
    )


@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_bill(
        db,
        bill_data,
        current_user,
    )
  


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_bill(
        db,
        bill_id,
        current_user,
    )


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_bill(
        db,
        bill_id,
        bill_data,
        current_user,
    )
    


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_bill(
        db,
        bill_id,
        current_user,
    )
