from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, field_validator


TransactionType = Literal["income", "expense"]
RecurrenceType = Literal["daily", "weekly", "monthly", "yearly"]


class TransactionCreate(BaseModel):
    category_id: str | None = None
    type: TransactionType
    amount: Decimal
    description: str | None = None
    notes: str | None = None
    transaction_date: date
    is_recurring: bool = False
    recurrence: RecurrenceType | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v

    @field_validator("recurrence")
    @classmethod
    def recurrence_requires_recurring(cls, v: RecurrenceType | None, info) -> RecurrenceType | None:
        if info.data.get("is_recurring") and v is None:
            raise ValueError("Si is_recurring es True debes indicar la recurrencia")
        return v


class TransactionUpdate(BaseModel):
    category_id: str | None = None
    amount: Decimal | None = None
    description: str | None = None
    notes: str | None = None
    transaction_date: date | None = None
    is_recurring: bool | None = None
    recurrence: RecurrenceType | None = None


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    category_id: str | None
    type: TransactionType
    amount: Decimal
    description: str | None
    notes: str | None
    transaction_date: date
    is_recurring: bool
    recurrence: RecurrenceType | None
    created_at: datetime
    updated_at: datetime