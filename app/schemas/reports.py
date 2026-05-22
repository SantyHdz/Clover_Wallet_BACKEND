from decimal import Decimal
from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    category_id: str | None
    category_name: str
    total: Decimal
    count: int


class MonthlySummary(BaseModel):
    year: int
    month: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class FinancialSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    total_debt: Decimal           # lo que el usuario debe
    total_debt_paid: Decimal      # lo que ya pagó de sus deudas
    total_debt_pending: Decimal   # lo que aún debe
    total_loan: Decimal           # lo que le deben al usuario
    total_loan_recovered: Decimal # lo que ya recuperó
    total_loan_pending: Decimal   # lo que aún le deben