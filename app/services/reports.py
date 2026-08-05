from sqlalchemy import func

from app.models.bill import Bill
from app.models.invoice import Invoice
from app.schemas.reports import (
    IncomeExpenseResponse,
    ProfitLossResponse,
    TaxSummaryResponse,
)

async def profit_loss_report(db, company_id, start_date, end_date, current_user):
    income = (db.query(func.sum(Invoice.total)).filter(Invoice.company_id == company_id, Invoice.user_id == current_user.id, Invoice.issue_date >= start_date, Invoice.issue_date <= end_date, Invoice.status != "cancelled").scalar() or 0)
    expenses = (db.query(func.sum(Bill.total)).filter(Bill.company_id == company_id, Bill.user_id == current_user.id, Bill.issue_date >= start_date, Bill.issue_date <= end_date, Bill.status != "cancelled").scalar() or 0)
    return ProfitLossResponse(
        income_total=income,
        expense_total=expenses,
        profit_loss=income - expenses,
        income_by_category=[],
        expense_by_category=[],
        period={"start": start_date, "end": end_date},
    )

async def income_expense_report(db, company_id, start_date, end_date, current_user):
    income = (db.query(func.sum(Invoice.total)).filter(Invoice.company_id == company_id, Invoice.issue_date >= start_date, Invoice.issue_date <= end_date, Invoice.status != "cancelled").scalar() or 0)
    expenses = (db.query(func.sum(Bill.total)).filter(Bill.company_id == company_id, Bill.issue_date >= start_date, Bill.issue_date <= end_date, Bill.status != "cancelled").scalar() or 0)
    return IncomeExpenseResponse(
        income_total=income,
        expense_total=expenses,
        net_income=income - expenses,
        period={"start": start_date, "end": end_date},
    )

async def tax_summary_report(db, company_id, start_date, end_date, current_user):
    return TaxSummaryResponse(
        tax_collected=0,
        tax_paid=0,
        net_tax=0,
        by_tax_rate=[],
        period={"start": start_date, "end": end_date},
    )