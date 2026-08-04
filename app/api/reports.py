from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.auth.user import User
from app.models.invoice import Invoice
from app.models.bill import Bill
from app.schemas.reports import (
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
    income = (
        db.query(func.sum(Invoice.total))
        .filter(
            Invoice.company_id == request.company_id,
            Invoice.issue_date >= request.start_date,
            Invoice.issue_date <= request.end_date,
            Invoice.status != "cancelled",
        )
        .scalar()
        or 0
    )

    expenses = (
        db.query(func.sum(Bill.total))
        .filter(
            Bill.company_id == request.company_id,
            Bill.issue_date >= request.start_date,
            Bill.issue_date <= request.end_date,
            Bill.status != "cancelled",
        )
        .scalar()
        or 0
    )

    return ProfitLossResponse(
        income_total=income,
        expense_total=expenses,
        profit_loss=income - expenses,
        income_by_category=[],
        expense_by_category=[],
        period={"start": request.start_date, "end": request.end_date},
    )


@router.post("/income-expense", response_model=IncomeExpenseResponse)
def income_expense_report(
    request: IncomeExpenseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    income = (
        db.query(func.sum(Invoice.total))
        .filter(
            Invoice.company_id == request.company_id,
            Invoice.issue_date >= request.start_date,
            Invoice.issue_date <= request.end_date,
            Invoice.status != "cancelled",
        )
        .scalar()
        or 0
    )

    expenses = (
        db.query(func.sum(Bill.total))
        .filter(
            Bill.company_id == request.company_id,
            Bill.issue_date >= request.start_date,
            Bill.issue_date <= request.end_date,
            Bill.status != "cancelled",
        )
        .scalar()
        or 0
    )

    return IncomeExpenseResponse(
        income_total=income,
        expense_total=expenses,
        net_income=income - expenses,
        period={"start": request.start_date, "end": request.end_date},
    )


@router.post("/tax-summary", response_model=TaxSummaryResponse)
def tax_summary_report(
    request: TaxSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaxSummaryResponse(
        tax_collected=0,
        tax_paid=0,
        net_tax=0,
        by_tax_rate=[],
        period={"start": request.start_date, "end": request.end_date},
    )