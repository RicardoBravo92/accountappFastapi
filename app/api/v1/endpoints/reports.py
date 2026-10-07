
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.permissions import (
    REPORT_PERMISSIONS,
    require_permission,
)
from app.models.auth.user import User
from app.schemas.reports import (
    IncomeExpenseRequest,
    IncomeExpenseResponse,
    ProfitLossRequest,
    ProfitLossResponse,
    TaxSummaryRequest,
    TaxSummaryResponse,
)
from app.services.reports import (
    income_expense_report,
    profit_loss_report,
    tax_summary_report,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/profit-loss", response_model=ProfitLossResponse)
def profit_loss_endpoint(
    request: ProfitLossRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(REPORT_PERMISSIONS["read"])),
):
    return profit_loss_report(
        db, request.company_id, request.start_date, request.end_date, current_user
    )


@router.post("/income-expense", response_model=IncomeExpenseResponse)
def income_expense_endpoint(
    request: IncomeExpenseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(REPORT_PERMISSIONS["read"])),
):
    return income_expense_report(
        db, request.company_id, request.start_date, request.end_date, current_user
    )


@router.post("/tax-summary", response_model=TaxSummaryResponse)
def tax_summary_endpoint(
    request: TaxSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(REPORT_PERMISSIONS["read"])),
):
    return tax_summary_report(
        db, request.company_id, request.start_date, request.end_date, current_user
    )
