from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, field_validator


SavingType = Literal["goal", "free"]
SavingStatus = Literal["active", "completed", "paused"]


class SavingCreate(BaseModel):
    name: str
    description: str | None = None
    type: SavingType = "goal"
    target_amount: Decimal | None = None
    target_date: date | None = None
    icon: str | None = None
    color: str | None = None

    @field_validator("target_amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("El monto objetivo debe ser mayor a 0")
        return v


class SavingUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    target_amount: Decimal | None = None
    target_date: date | None = None
    status: SavingStatus | None = None
    icon: str | None = None
    color: str | None = None


class SavingResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None
    type: SavingType
    target_amount: Decimal | None
    current_amount: Decimal
    target_date: date | None
    status: SavingStatus
    icon: str | None
    color: str | None
    created_at: datetime
    updated_at: datetime


# ── Aportes 

class ContributionCreate(BaseModel):
    amount: Decimal
    note: str | None = None
    contribution_date: date

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El aporte debe ser mayor a 0")
        return v


class ContributionResponse(BaseModel):
    id: str
    saving_id: str
    user_id: str
    amount: Decimal
    note: str | None
    contribution_date: date
    created_at: datetime


# Resumen

class SavingSummary(BaseModel):
    total_saved: Decimal
    total_goal: Decimal
    savings_count: int
    completed_count: int
    active_count: int


class MonthlyContribution(BaseModel):
    year: int
    month: int
    total: Decimal


class SavingProjection(BaseModel):
    saving_id: str
    name: str
    current_amount: Decimal
    target_amount: Decimal | None
    monthly_average: Decimal
    projected_date: date | None
    months_remaining: int | None