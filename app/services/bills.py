

from sqlalchemy.orm import Session

from app.models.auth.user import User
from app.models.bill import Bill, BillStatus
from app.schemas.bill import BillCreate, BillResponse, BillUpdate


async def get_all_bills(
        db: Session,
        company_id: int,
        status: str | None = None,
        vendor_id: int | None = None,
        current_user: User = None,
    ) -> list[BillResponse]:
        query = db.query(Bill).filter(Bill.company_id == company_id)
        if status:
            query = query.filter(Bill.status == status)
        if vendor_id:
            query = query.filter(Bill.vendor_id == vendor_id)
        return query.order_by(Bill.due_date.desc()).all()

async def get_bill(
        db: Session,
        bill_id: int,
        current_user: User = None,
    ) -> BillResponse | None:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        return bill

async def create_bill(
        db: Session,
        bill_data: BillCreate,
        current_user: User = None,
    ) -> BillResponse:
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

async def update_bill(
        db: Session,
        bill_id: int,
        bill_data: BillUpdate,
        current_user: User = None,
    ) -> BillResponse | None:
        bill = get_bill(db, bill_id, current_user)
        update_data = bill_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(bill, key, value)
        db.commit()
        db.refresh(bill)
        return BillResponse(**bill.__dict__)

async def delete_bill(
        db: Session,
        bill_id: int,
        current_user: User = None,
    ) -> None:
        bill = get_bill(db, bill_id, current_user)
        db.delete(bill)
        db.commit()


bills_service = {
    "get_all_bills": get_all_bills,
    "get_bill": get_bill,
    "create_bill": create_bill,
    "update_bill": update_bill,
    "delete_bill": delete_bill,
}
