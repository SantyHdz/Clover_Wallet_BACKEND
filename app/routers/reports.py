from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.reports import CategoryBreakdown, FinancialSummary, MonthlySummary
from app.services import reports as reports_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=FinancialSummary)
def get_summary(user: dict = Depends(get_current_user)):
    return reports_service.get_financial_summary(user["sub"])


@router.get("/monthly", response_model=list[MonthlySummary])
def get_monthly(year: int, user: dict = Depends(get_current_user)):
    return reports_service.get_monthly_summary(user["sub"], year)


@router.get("/breakdown", response_model=list[CategoryBreakdown])
def get_breakdown(
    type: str,
    year: int | None = None,
    month: int | None = None,
    user: dict = Depends(get_current_user),
):
    return reports_service.get_category_breakdown(user["sub"], type, year, month)