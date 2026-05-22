from decimal import Decimal
from app.core.supabase import get_supabase_admin
from app.schemas.reports import CategoryBreakdown, FinancialSummary, MonthlySummary


def get_financial_summary(user_id: str) -> FinancialSummary:
    admin = get_supabase_admin()

    # Totales de transacciones
    transactions = (
        admin.table("transactions")
        .select("type, amount")
        .eq("user_id", user_id)
        .execute()
    ).data

    total_income = sum(Decimal(str(t["amount"])) for t in transactions if t["type"] == "income")
    total_expense = sum(Decimal(str(t["amount"])) for t in transactions if t["type"] == "expense")

    # Totales de deudas
    debts = (
        admin.table("debts")
        .select("total_amount, paid_amount")
        .eq("user_id", user_id)
        .execute()
    ).data

    total_debt = sum(Decimal(str(d["total_amount"])) for d in debts)
    total_debt_paid = sum(Decimal(str(d["paid_amount"])) for d in debts)

    # Totales de préstamos
    loans = (
        admin.table("loans")
        .select("total_amount, recovered_amount")
        .eq("user_id", user_id)
        .execute()
    ).data

    total_loan = sum(Decimal(str(l["total_amount"])) for l in loans)
    total_loan_recovered = sum(Decimal(str(l["recovered_amount"])) for l in loans)

    return FinancialSummary(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        total_debt=total_debt,
        total_debt_paid=total_debt_paid,
        total_debt_pending=total_debt - total_debt_paid,
        total_loan=total_loan,
        total_loan_recovered=total_loan_recovered,
        total_loan_pending=total_loan - total_loan_recovered,
    )


def get_monthly_summary(user_id: str, year: int) -> list[MonthlySummary]:
    admin = get_supabase_admin()

    from datetime import date
    start = date(year, 1, 1).isoformat()
    end = date(year + 1, 1, 1).isoformat()

    transactions = (
        admin.table("transactions")
        .select("type, amount, transaction_date")
        .eq("user_id", user_id)
        .gte("transaction_date", start)
        .lt("transaction_date", end)
        .execute()
    ).data

    # Agrupar por mes manualmente
    months: dict[int, dict] = {
        m: {"income": Decimal("0"), "expense": Decimal("0")}
        for m in range(1, 13)
    }

    for t in transactions:
        month = int(t["transaction_date"][5:7])
        amount = Decimal(str(t["amount"]))
        months[month][t["type"]] += amount

    return [
        MonthlySummary(
            year=year,
            month=m,
            total_income=months[m]["income"],
            total_expense=months[m]["expense"],
            balance=months[m]["income"] - months[m]["expense"],
        )
        for m in range(1, 13)
    ]


def get_category_breakdown(
    user_id: str,
    type: str,
    year: int | None = None,
    month: int | None = None,
) -> list[CategoryBreakdown]:
    admin = get_supabase_admin()

    from datetime import date

    query = (
        admin.table("transactions")
        .select("amount, category_id, categories(name)")
        .eq("user_id", user_id)
        .eq("type", type)
    )

    if year and month:
        start = date(year, month, 1).isoformat()
        end = date(year + 1, 1, 1).isoformat() if month == 12 else date(year, month + 1, 1).isoformat()
        query = query.gte("transaction_date", start).lt("transaction_date", end)
    elif year:
        start = date(year, 1, 1).isoformat()
        end = date(year + 1, 1, 1).isoformat()
        query = query.gte("transaction_date", start).lt("transaction_date", end)

    transactions = query.execute().data

    # Agrupar por categoría
    groups: dict[str, dict] = {}
    for t in transactions:
        cat_id = t["category_id"] or "sin_categoria"
        cat_name = (
            t["categories"]["name"] if t.get("categories") else "Sin categoría"
        )
        if cat_id not in groups:
            groups[cat_id] = {"name": cat_name, "total": Decimal("0"), "count": 0}
        groups[cat_id]["total"] += Decimal(str(t["amount"]))
        groups[cat_id]["count"] += 1

    return sorted(
        [
            CategoryBreakdown(
                category_id=k if k != "sin_categoria" else None,
                category_name=v["name"],
                total=v["total"],
                count=v["count"],
            )
            for k, v in groups.items()
        ],
        key=lambda x: x.total,
        reverse=True,
    )