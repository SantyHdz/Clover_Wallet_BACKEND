from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.supabase import get_supabase_admin
from app.schemas.debts import (
    DebtCreate,
    DebtPaymentCreate,
    DebtPaymentResponse,
    DebtResponse,
    DebtUpdate,
)


def get_debts(user_id: str, status: str | None = None) -> list[DebtResponse]:
    admin = get_supabase_admin()

    query = (
        admin.table("debts")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )

    if status:
        query = query.eq("status", status)

    result = query.execute()
    return [DebtResponse(**row) for row in result.data]


def get_debt(user_id: str, debt_id: str) -> DebtResponse:
    admin = get_supabase_admin()

    result = (
        admin.table("debts")
        .select("*")
        .eq("id", debt_id)
        .single()
        .execute()
    )

    if not result.data:
        raise NotFoundError("Deuda no encontrada")
    if result.data["user_id"] != user_id:
        raise ForbiddenError("No tienes acceso a esta deuda")

    return DebtResponse(**result.data)


def create_debt(user_id: str, data: DebtCreate) -> DebtResponse:
    admin = get_supabase_admin()

    payload = {
        **data.model_dump(),
        "user_id": user_id,
        "due_date": data.due_date.isoformat() if data.due_date else None,
        "total_amount": str(data.total_amount),
        "interest_rate": str(data.interest_rate),
    }

    result = admin.table("debts").insert(payload).execute()
    return DebtResponse(**result.data[0])


def update_debt(user_id: str, debt_id: str, data: DebtUpdate) -> DebtResponse:
    admin = get_supabase_admin()

    get_debt(user_id, debt_id)

    payload = data.model_dump(exclude_none=True)
    if "due_date" in payload and payload["due_date"]:
        payload["due_date"] = payload["due_date"].isoformat()
    if "total_amount" in payload:
        payload["total_amount"] = str(payload["total_amount"])
    if "interest_rate" in payload:
        payload["interest_rate"] = str(payload["interest_rate"])

    result = (
        admin.table("debts")
        .update(payload)
        .eq("id", debt_id)
        .execute()
    )

    return DebtResponse(**result.data[0])


def delete_debt(user_id: str, debt_id: str) -> None:
    admin = get_supabase_admin()
    get_debt(user_id, debt_id)
    admin.table("debts").delete().eq("id", debt_id).execute()


# ── Pagos ──────────────────────────────────────────────────────────────────────

def get_debt_payments(user_id: str, debt_id: str) -> list[DebtPaymentResponse]:
    admin = get_supabase_admin()

    get_debt(user_id, debt_id)

    result = (
        admin.table("debt_payments")
        .select("*")
        .eq("debt_id", debt_id)
        .order("payment_date", desc=True)
        .execute()
    )

    return [DebtPaymentResponse(**row) for row in result.data]


def create_debt_payment(
    user_id: str, debt_id: str, data: DebtPaymentCreate
) -> DebtPaymentResponse:
    admin = get_supabase_admin()

    get_debt(user_id, debt_id)

    payload = {
        "debt_id": debt_id,
        "user_id": user_id,
        "amount": str(data.amount),
        "payment_date": data.payment_date.isoformat(),
        "notes": data.notes,
    }

    result = admin.table("debt_payments").insert(payload).execute()
    # El trigger de BD actualiza paid_amount y status automáticamente
    return DebtPaymentResponse(**result.data[0])


def delete_debt_payment(user_id: str, debt_id: str, payment_id: str) -> None:
    admin = get_supabase_admin()

    get_debt(user_id, debt_id)

    result = (
        admin.table("debt_payments")
        .select("id, user_id")
        .eq("id", payment_id)
        .single()
        .execute()
    )

    if not result.data:
        raise NotFoundError("Pago no encontrado")
    if result.data["user_id"] != user_id:
        raise ForbiddenError("No tienes acceso a este pago")

    admin.table("debt_payments").delete().eq("id", payment_id).execute()