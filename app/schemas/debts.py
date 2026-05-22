from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, field_validator


DebtStatus = Literal["pending", "partial", "paid", "overdue"]


class DebtCreate(BaseModel):
    creditor_name: str
    description: str | None = None
    total_amount: Decimal
    interest_rate: Decimal = Decimal("0")
    due_date: date | None = None

    @field_validator("total_amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class DebtUpdate(BaseModel):
    creditor_name: str | None = None
    description: str | None = None
    total_amount: Decimal | None = None
    interest_rate: Decimal | None = None
    due_date: date | None = None


class DebtResponse(BaseModel):
    id: str
    user_id: str
    creditor_name: str
    description: str | None
    total_amount: Decimal
    paid_amount: Decimal
    interest_rate: Decimal
    due_date: date | None
    status: DebtStatus
    created_at: datetime
    updated_at: datetime


# ── Pagos de deuda ─────────────────────────────────────────────────────────────

class DebtPaymentCreate(BaseModel):
    amount: Decimal
    payment_date: date
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class DebtPaymentResponse(BaseModel):
    id: str
    debt_id: str
    user_id: str
    amount: Decimal
    payment_date: date
    notes: str | None
    created_at: datetime