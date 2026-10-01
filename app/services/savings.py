from datetime import date, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.supabase import get_supabase_admin
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


# ── Helpers 

def _fmt(v) -> str:
    return str(v) if v is not None else None


def _get_saving(admin, user_id: str, saving_id: str) -> dict:
    result = (
        admin.table("savings")
        .select("*")
        .eq("id", saving_id)
        .single()
        .execute()
    )
    if not result.data:
        raise NotFoundError("Ahorro no encontrado")
    if result.data["user_id"] != user_id:
        raise ForbiddenError("No tienes acceso a este ahorro")
    return result.data


# ── CRUD Savings

def get_savings(user_id: str, status: str | None = None) -> list[SavingResponse]:
    admin = get_supabase_admin()
    query = (
        admin.table("savings")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )
    if status:
        query = query.eq("status", status)
    result = query.execute()
    return [SavingResponse(**row) for row in result.data]


def get_saving(user_id: str, saving_id: str) -> SavingResponse:
    admin = get_supabase_admin()
    return SavingResponse(**_get_saving(admin, user_id, saving_id))


def create_saving(user_id: str, data: SavingCreate) -> SavingResponse:
    admin = get_supabase_admin()
    payload = {
        "user_id": user_id,
        "name": data.name,
        "description": data.description,
        "type": data.type,
        "target_amount": _fmt(data.target_amount),
        "target_date": data.target_date.isoformat() if data.target_date else None,
        "icon": data.icon,
        "color": data.color,
    }
    result = admin.table("savings").insert(payload).execute()
    return SavingResponse(**result.data[0])


def update_saving(user_id: str, saving_id: str, data: SavingUpdate) -> SavingResponse:
    admin = get_supabase_admin()
    _get_saving(admin, user_id, saving_id)

    payload = data.model_dump(exclude_none=True)
    if "target_amount" in payload:
        payload["target_amount"] = _fmt(payload["target_amount"])
    if "target_date" in payload and payload["target_date"]:
        payload["target_date"] = payload["target_date"].isoformat()

    result = (
        admin.table("savings")
        .update(payload)
        .eq("id", saving_id)
        .execute()
    )
    return SavingResponse(**result.data[0])


def delete_saving(user_id: str, saving_id: str) -> None:
    admin = get_supabase_admin()
    _get_saving(admin, user_id, saving_id)
    admin.table("savings").delete().eq("id", saving_id).execute()


# ── Contributions ──────────────────────────────────────────────────────────────

def get_contributions(user_id: str, saving_id: str) -> list[ContributionResponse]:
    admin = get_supabase_admin()
    _get_saving(admin, user_id, saving_id)
    result = (
        admin.table("saving_contributions")
        .select("*")
        .eq("saving_id", saving_id)
        .order("contribution_date", desc=True)
        .execute()
    )
    return [ContributionResponse(**row) for row in result.data]


def create_contribution(
    user_id: str, saving_id: str, data: ContributionCreate
) -> ContributionResponse:
    admin = get_supabase_admin()
    _get_saving(admin, user_id, saving_id)
    payload = {
        "saving_id": saving_id,
        "user_id": user_id,
        "amount": _fmt(data.amount),
        "note": data.note,
        "contribution_date": data.contribution_date.isoformat(),
    }
    result = admin.table("saving_contributions").insert(payload).execute()
    return ContributionResponse(**result.data[0])


def delete_contribution(
    user_id: str, saving_id: str, contribution_id: str
) -> None:
    admin = get_supabase_admin()
    _get_saving(admin, user_id, saving_id)
    result = (
        admin.table("saving_contributions")
        .select("id, user_id")
        .eq("id", contribution_id)
        .single()
        .execute()
    )
    if not result.data:
        raise NotFoundError("Aporte no encontrado")
    if result.data["user_id"] != user_id:
        raise ForbiddenError("No tienes acceso a este aporte")
    admin.table("saving_contributions").delete().eq("id", contribution_id).execute()


# ── Summary & Analytics ────────────────────────────────────────────────────────

def get_summary(user_id: str) -> SavingSummary:
    admin = get_supabase_admin()
    savings = (
        admin.table("savings")
        .select("current_amount, target_amount, status, type")
        .eq("user_id", user_id)
        .execute()
    ).data

    total_saved = sum(Decimal(str(s["current_amount"])) for s in savings)
    total_goal = sum(
        Decimal(str(s["target_amount"]))
        for s in savings
        if s["type"] == "goal" and s["target_amount"] and s["status"] == "active"
    )

    return SavingSummary(
        total_saved=total_saved,
        total_goal=total_goal,
        savings_count=len(savings),
        completed_count=sum(1 for s in savings if s["status"] == "completed"),
        active_count=sum(1 for s in savings if s["status"] == "active"),
    )


def get_monthly_contributions(
    user_id: str, saving_id: str, year: int
) -> list[MonthlyContribution]:
    admin = get_supabase_admin()
    _get_saving(admin, user_id, saving_id)

    start = date(year, 1, 1).isoformat()
    end = date(year + 1, 1, 1).isoformat()

    contributions = (
        admin.table("saving_contributions")
        .select("amount, contribution_date")
        .eq("saving_id", saving_id)
        .gte("contribution_date", start)
        .lt("contribution_date", end)
        .execute()
    ).data

    months: dict[int, Decimal] = {m: Decimal("0") for m in range(1, 13)}
    for c in contributions:
        m = int(c["contribution_date"][5:7])
        months[m] += Decimal(str(c["amount"]))

    return [
        MonthlyContribution(year=year, month=m, total=months[m])
        for m in range(1, 13)
    ]


def get_projections(user_id: str) -> list[SavingProjection]:
    admin = get_supabase_admin()

    savings = (
        admin.table("savings")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    ).data

    projections = []
    today = date.today()

    for s in savings:
        saving_id = s["id"]
        current = Decimal(str(s["current_amount"]))
        target = Decimal(str(s["target_amount"])) if s["target_amount"] else None

        # Calcular promedio mensual de los últimos 3 meses
        three_months_ago = (today - timedelta(days=90)).isoformat()
        recent = (
            admin.table("saving_contributions")
            .select("amount")
            .eq("saving_id", saving_id)
            .gte("contribution_date", three_months_ago)
            .execute()
        ).data

        total_recent = sum(Decimal(str(c["amount"])) for c in recent)
        monthly_avg = total_recent / 3 if total_recent > 0 else Decimal("0")

        projected_date = None
        months_remaining = None

        if target and target > current and monthly_avg > 0:
            remaining = target - current
            months_needed = int((remaining / monthly_avg).to_integral_value()) + 1
            projected_date = today + relativedelta(months=months_needed)
            months_remaining = months_needed

        projections.append(SavingProjection(
            saving_id=saving_id,
            name=s["name"],
            current_amount=current,
            target_amount=target,
            monthly_average=monthly_avg,
            projected_date=projected_date,
            months_remaining=months_remaining,
        ))

    return projections