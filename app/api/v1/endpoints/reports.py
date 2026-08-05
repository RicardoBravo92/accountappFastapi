from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.auth.user import User
from app.schemas.reports import (
    IncomeExpenseRequest,
    IncomeExpenseResponse,
    ProfitLossRequest,
    ProfitLossResponse,
    TaxSummaryRequest,
    TaxSummaryResponse,
)
from app.services.reports import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/profit-loss", response_model=ProfitLossResponse)
def profit_loss(
    request: ProfitLossRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service["profit_loss_report"](
        db, request.company_id, request.start_date, request.end_date, current_user
    )


@router.post("/income-expense", response_model=IncomeExpenseResponse)
def income_expense(
    request: IncomeExpenseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service["income_expense_report"](
        db, request.company_id, request.start_date, request.end_date, current_user
    )


@router.post("/tax-summary", response_model=TaxSummaryResponse)
def tax_summary(
    request: TaxSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return report_service["tax_summary_report"](
        db, request.company_id, request.start_date, request.end_date, current_user
    )
