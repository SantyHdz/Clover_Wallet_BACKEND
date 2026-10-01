from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.savings import (
    ContributionCreate,
    ContributionResponse,
    MonthlyContribution,
    SavingCreate,
    SavingProjection,
    SavingResponse,
    SavingSummary,
    SavingUpdate,
)
from app.services import savings as savings_service

router = APIRouter(prefix="/savings", tags=["Savings"])


# ── CRUD

@router.get("/", response_model=list[SavingResponse])
def get_savings(status: str | None = None, user: dict = Depends(get_current_user)):
    return savings_service.get_savings(user["sub"], status)


@router.get("/summary", response_model=SavingSummary)
def get_summary(user: dict = Depends(get_current_user)):
    return savings_service.get_summary(user["sub"])


@router.get("/projections", response_model=list[SavingProjection])
def get_projections(user: dict = Depends(get_current_user)):
    return savings_service.get_projections(user["sub"])


@router.get("/{saving_id}", response_model=SavingResponse)
def get_saving(saving_id: str, user: dict = Depends(get_current_user)):
    return savings_service.get_saving(user["sub"], saving_id)


@router.post("/", response_model=SavingResponse, status_code=201)
def create_saving(data: SavingCreate, user: dict = Depends(get_current_user)):
    return savings_service.create_saving(user["sub"], data)


@router.patch("/{saving_id}", response_model=SavingResponse)
def update_saving(saving_id: str, data: SavingUpdate, user: dict = Depends(get_current_user)):
    return savings_service.update_saving(user["sub"], saving_id, data)


@router.delete("/{saving_id}", status_code=204)
def delete_saving(saving_id: str, user: dict = Depends(get_current_user)):
    savings_service.delete_saving(user["sub"], saving_id)


# ── Contributions

@router.get("/{saving_id}/contributions", response_model=list[ContributionResponse])
def get_contributions(saving_id: str, user: dict = Depends(get_current_user)):
    return savings_service.get_contributions(user["sub"], saving_id)


@router.post("/{saving_id}/contributions", response_model=ContributionResponse, status_code=201)
def create_contribution(
    saving_id: str,
    data: ContributionCreate,
    user: dict = Depends(get_current_user),
):
    return savings_service.create_contribution(user["sub"], saving_id, data)


@router.delete("/{saving_id}/contributions/{contribution_id}", status_code=204)
def delete_contribution(
    saving_id: str,
    contribution_id: str,
    user: dict = Depends(get_current_user),
):
    savings_service.delete_contribution(user["sub"], saving_id, contribution_id)


# ── Analytics

@router.get("/{saving_id}/monthly", response_model=list[MonthlyContribution])
def get_monthly(
    saving_id: str,
    year: int,
    user: dict = Depends(get_current_user),
):
    return savings_service.get_monthly_contributions(user["sub"], saving_id, year)