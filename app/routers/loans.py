from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.loans import (
    LoanCreate,
    LoanPaymentCreate,
    LoanPaymentResponse,
    LoanResponse,
    LoanUpdate,
)
from app.services import loans as loans_service

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get("/", response_model=list[LoanResponse])
def get_loans(status: str | None = None, user: dict = Depends(get_current_user)):
    return loans_service.get_loans(user["sub"], status)


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: str, user: dict = Depends(get_current_user)):
    return loans_service.get_loan(user["sub"], loan_id)


@router.post("/", response_model=LoanResponse, status_code=201)
def create_loan(data: LoanCreate, user: dict = Depends(get_current_user)):
    return loans_service.create_loan(user["sub"], data)


@router.patch("/{loan_id}", response_model=LoanResponse)
def update_loan(loan_id: str, data: LoanUpdate, user: dict = Depends(get_current_user)):
    return loans_service.update_loan(user["sub"], loan_id, data)


@router.delete("/{loan_id}", status_code=204)
def delete_loan(loan_id: str, user: dict = Depends(get_current_user)):
    loans_service.delete_loan(user["sub"], loan_id)


# ── Cobros ─────────────────────────────────────────────────────────────────────

@router.get("/{loan_id}/payments", response_model=list[LoanPaymentResponse])
def get_payments(loan_id: str, user: dict = Depends(get_current_user)):
    return loans_service.get_loan_payments(user["sub"], loan_id)


@router.post("/{loan_id}/payments", response_model=LoanPaymentResponse, status_code=201)
def create_payment(
    loan_id: str,
    data: LoanPaymentCreate,
    user: dict = Depends(get_current_user),
):
    return loans_service.create_loan_payment(user["sub"], loan_id, data)


@router.delete("/{loan_id}/payments/{payment_id}", status_code=204)
def delete_payment(
    loan_id: str,
    payment_id: str,
    user: dict = Depends(get_current_user),
):
    loans_service.delete_loan_payment(user["sub"], loan_id, payment_id)