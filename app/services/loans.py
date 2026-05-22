from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.supabase import get_supabase_admin
from app.schemas.loans import (
    LoanCreate,
    LoanPaymentCreate,
    LoanPaymentResponse,
    LoanResponse,
    LoanUpdate,
)


def get_loans(user_id: str, status: str | None = None) -> list[LoanResponse]:
    admin = get_supabase_admin()

    query = (
        admin.table("loans")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )

    if status:
        query = query.eq("status", status)

    result = query.execute()
    return [LoanResponse(**row) for row in result.data]


def get_loan(user_id: str, loan_id: str) -> LoanResponse:
    admin = get_supabase_admin()

    result = (
        admin.table("loans")
        .select("*")
        .eq("id", loan_id)
        .single()
        .execute()
    )

    if not result.data:
        raise NotFoundError("Préstamo no encontrado")
    if result.data["user_id"] != user_id:
        raise ForbiddenError("No tienes acceso a este préstamo")

    return LoanResponse(**result.data)


def create_loan(user_id: str, data: LoanCreate) -> LoanResponse:
    admin = get_supabase_admin()

    payload = {
        **data.model_dump(),
        "user_id": user_id,
        "due_date": data.due_date.isoformat() if data.due_date else None,
        "total_amount": str(data.total_amount),
        "interest_rate": str(data.interest_rate),
    }

    result = admin.table("loans").insert(payload).execute()
    return LoanResponse(**result.data[0])


def update_loan(user_id: str, loan_id: str, data: LoanUpdate) -> LoanResponse:
    admin = get_supabase_admin()

    get_loan(user_id, loan_id)

    payload = data.model_dump(exclude_none=True)
    if "due_date" in payload and payload["due_date"]:
        payload["due_date"] = payload["due_date"].isoformat()
    if "total_amount" in payload:
        payload["total_amount"] = str(payload["total_amount"])
    if "interest_rate" in payload:
        payload["interest_rate"] = str(payload["interest_rate"])

    result = (
        admin.table("loans")
        .update(payload)
        .eq("id", loan_id)
        .execute()
    )

    return LoanResponse(**result.data[0])


def delete_loan(user_id: str, loan_id: str) -> None:
    admin = get_supabase_admin()
    get_loan(user_id, loan_id)
    admin.table("loans").delete().eq("id", loan_id).execute()


# ── Cobros ─────────────────────────────────────────────────────────────────────

def get_loan_payments(user_id: str, loan_id: str) -> list[LoanPaymentResponse]:
    admin = get_supabase_admin()

    get_loan(user_id, loan_id)

    result = (
        admin.table("loan_payments")
        .select("*")
        .eq("loan_id", loan_id)
        .order("payment_date", desc=True)
        .execute()
    )

    return [LoanPaymentResponse(**row) for row in result.data]


def create_loan_payment(
    user_id: str, loan_id: str, data: LoanPaymentCreate
) -> LoanPaymentResponse:
    admin = get_supabase_admin()

    get_loan(user_id, loan_id)

    payload = {
        "loan_id": loan_id,
        "user_id": user_id,
        "amount": str(data.amount),
        "payment_date": data.payment_date.isoformat(),
        "notes": data.notes,
    }

    result = admin.table("loan_payments").insert(payload).execute()
    # El trigger de BD actualiza recovered_amount y status automáticamente
    return LoanPaymentResponse(**result.data[0])


def delete_loan_payment(user_id: str, loan_id: str, payment_id: str) -> None:
    admin = get_supabase_admin()

    get_loan(user_id, loan_id)

    result = (
        admin.table("loan_payments")
        .select("id, user_id")
        .eq("id", payment_id)
        .single()
        .execute()
    )

    if not result.data:
        raise NotFoundError("Cobro no encontrado")
    if result.data["user_id"] != user_id:
        raise ForbiddenError("No tienes acceso a este cobro")

    admin.table("loan_payments").delete().eq("id", payment_id).execute()