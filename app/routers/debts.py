from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.debts import (
    DebtCreate,
    DebtPaymentCreate,
    DebtPaymentResponse,
    DebtResponse,
    DebtUpdate,
)
from app.services import debts as debts_service

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.get("/", response_model=list[DebtResponse])
def get_debts(status: str | None = None, user: dict = Depends(get_current_user)):
    return debts_service.get_debts(user["sub"], status)


@router.get("/{debt_id}", response_model=DebtResponse)
def get_debt(debt_id: str, user: dict = Depends(get_current_user)):
    return debts_service.get_debt(user["sub"], debt_id)


@router.post("/", response_model=DebtResponse, status_code=201)
def create_debt(data: DebtCreate, user: dict = Depends(get_current_user)):
    return debts_service.create_debt(user["sub"], data)


@router.patch("/{debt_id}", response_model=DebtResponse)
def update_debt(debt_id: str, data: DebtUpdate, user: dict = Depends(get_current_user)):
    return debts_service.update_debt(user["sub"], debt_id, data)


@router.delete("/{debt_id}", status_code=204)
def delete_debt(debt_id: str, user: dict = Depends(get_current_user)):
    debts_service.delete_debt(user["sub"], debt_id)


# ── Pagos ──────────────────────────────────────────────────────────────────────

@router.get("/{debt_id}/payments", response_model=list[DebtPaymentResponse])
def get_payments(debt_id: str, user: dict = Depends(get_current_user)):
    return debts_service.get_debt_payments(user["sub"], debt_id)


@router.post("/{debt_id}/payments", response_model=DebtPaymentResponse, status_code=201)
def create_payment(
    debt_id: str,
    data: DebtPaymentCreate,
    user: dict = Depends(get_current_user),
):
    return debts_service.create_debt_payment(user["sub"], debt_id, data)


@router.delete("/{debt_id}/payments/{payment_id}", status_code=204)
def delete_payment(
    debt_id: str,
    payment_id: str,
    user: dict = Depends(get_current_user),
):
    debts_service.delete_debt_payment(user["sub"], debt_id, payment_id)