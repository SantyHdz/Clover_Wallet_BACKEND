from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.transactions import TransactionCreate, TransactionResponse, TransactionUpdate
from app.services import transactions as transactions_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    type: str | None = None,
    category_id: str | None = None,
    year: int | None = None,
    month: int | None = None,
    user: dict = Depends(get_current_user),
):
    return transactions_service.get_transactions(
        user_id=user["sub"],
        type=type,
        category_id=category_id,
        year=year,
        month=month,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, user: dict = Depends(get_current_user)):
    return transactions_service.get_transaction(user["sub"], transaction_id)


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(data: TransactionCreate, user: dict = Depends(get_current_user)):
    return transactions_service.create_transaction(user["sub"], data)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    user: dict = Depends(get_current_user),
):
    return transactions_service.update_transaction(user["sub"], transaction_id, data)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: str, user: dict = Depends(get_current_user)):
    transactions_service.delete_transaction(user["sub"], transaction_id)