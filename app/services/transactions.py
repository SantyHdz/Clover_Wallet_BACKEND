from datetime import date
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.supabase import get_supabase_admin
from app.schemas.transactions import TransactionCreate, TransactionResponse, TransactionUpdate


def get_transactions(
    user_id: str,
    type: str | None = None,
    category_id: str | None = None,
    year: int | None = None,
    month: int | None = None,
) -> list[TransactionResponse]:
    admin = get_supabase_admin()

    query = (
        admin.table("transactions")
        .select("*")
        .eq("user_id", user_id)
        .order("transaction_date", desc=True)
    )

    if type:
        query = query.eq("type", type)
    if category_id:
        query = query.eq("category_id", category_id)
    if year and month:
        # Filtrar por mes completo
        start = date(year, month, 1).isoformat()
        # Último día del mes
        if month == 12:
            end = date(year + 1, 1, 1).isoformat()
        else:
            end = date(year, month + 1, 1).isoformat()
        query = query.gte("transaction_date", start).lt("transaction_date", end)
    elif year:
        start = date(year, 1, 1).isoformat()
        end = date(year + 1, 1, 1).isoformat()
        query = query.gte("transaction_date", start).lt("transaction_date", end)

    result = query.execute()
    return [TransactionResponse(**row) for row in result.data]


def get_transaction(user_id: str, transaction_id: str) -> TransactionResponse:
    admin = get_supabase_admin()

    result = (
        admin.table("transactions")
        .select("*")
        .eq("id", transaction_id)
        .single()
        .execute()
    )

    if not result.data:
        raise NotFoundError("Transacción no encontrada")
    if result.data["user_id"] != user_id:
        raise ForbiddenError("No tienes acceso a esta transacción")

    return TransactionResponse(**result.data)


def create_transaction(user_id: str, data: TransactionCreate) -> TransactionResponse:
    admin = get_supabase_admin()

    payload = {
        "user_id": user_id,
        "category_id": data.category_id,
        "type": data.type,
        "amount": str(data.amount),
        "description": data.description,
        "notes": data.notes,
        "transaction_date": data.transaction_date.isoformat(),
        "is_recurring": data.is_recurring,
        "recurrence": data.recurrence,
    }

    result = admin.table("transactions").insert(payload).execute()
    return TransactionResponse(**result.data[0])

def update_transaction(
    user_id: str, transaction_id: str, data: TransactionUpdate
) -> TransactionResponse:
    admin = get_supabase_admin()

    # Verificar propiedad
    get_transaction(user_id, transaction_id)

    payload = data.model_dump(exclude_none=True)
    if "transaction_date" in payload:
        payload["transaction_date"] = payload["transaction_date"].isoformat()

    result = (
        admin.table("transactions")
        .update(payload)
        .eq("id", transaction_id)
        .execute()
    )

    return TransactionResponse(**result.data[0])


def delete_transaction(user_id: str, transaction_id: str) -> None:
    admin = get_supabase_admin()
    get_transaction(user_id, transaction_id)
    admin.table("transactions").delete().eq("id", transaction_id).execute()