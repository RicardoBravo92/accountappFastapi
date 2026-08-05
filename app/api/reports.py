
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.models.bill import Bill
from app.models.invoice import Invoice
from app.services.reports import (
    IncomeExpenseRequest,
    IncomeExpenseResponse,
    ProfitLossRequest,
    ProfitLossResponse,
    TaxSummaryRequest,
    TaxSummaryResponse,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/profit-loss", response_model=ProfitLossResponse)
def profit_loss_report(
    request: ProfitLossRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return profit_loss_report(db, request.company_id, request.start_date, request.end_date, current_user)


@router.post("/income-expense", response_model=IncomeExpenseResponse)
def income_expense_report(
    request: IncomeExpenseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return income_expense_report(db, request.company_id, request.start_date, request.end_date, current_user)

@router.post("/tax-summary", response_model=TaxSummaryResponse)
def tax_summary_report(
    request: TaxSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return tax_summary_report(db, request.company_id, request.start_date, request.end_date, current_user)
