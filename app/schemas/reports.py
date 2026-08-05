from datetime import datetime

from pydantic import BaseModel


class ProfitLossRequest(BaseModel):
    company_id: int
    start_date: datetime
    end_date: datetime
    currency_code: str | None = "USD"


class ProfitLossResponse(BaseModel):
    income_total: float
    expense_total: float
    profit_loss: float
    income_by_category: list[dict]
    expense_by_category: list[dict]
    period: dict


class IncomeExpenseRequest(BaseModel):
    company_id: int
    start_date: datetime
    end_date: datetime
    currency_code: str | None = "USD"


class IncomeExpenseResponse(BaseModel):
    income_total: float
    expense_total: float
    net_income: float
    period: dict


class TaxSummaryRequest(BaseModel):
    company_id: int
    start_date: datetime
    end_date: datetime
    currency_code: str | None = "USD"


class TaxSummaryResponse(BaseModel):
    tax_collected: float
    tax_paid: float
    net_tax: float
    by_tax_rate: list[dict]
    period: dict
