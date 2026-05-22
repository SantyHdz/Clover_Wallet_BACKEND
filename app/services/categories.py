from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.supabase import get_supabase_admin
from app.schemas.categories import CategoryCreate, CategoryResponse


def get_categories(user_id: str) -> list[CategoryResponse]:
    """Retorna las categorías globales + las propias del usuario."""
    admin = get_supabase_admin()

    result = (
        admin.table("categories")
        .select("*")
        .or_(f"user_id.is.null,user_id.eq.{user_id}")
        .order("is_global", desc=True)
        .order("name")
        .execute()
    )

    return [CategoryResponse(**row) for row in result.data]


def create_category(user_id: str, data: CategoryCreate) -> CategoryResponse:
    admin = get_supabase_admin()

    payload = {
        **data.model_dump(),
        "user_id": user_id,
        "is_global": False,
    }

    result = admin.table("categories").insert(payload).execute()
    return CategoryResponse(**result.data[0])


def delete_category(user_id: str, category_id: str) -> None:
    admin = get_supabase_admin()

    # Verificar que existe y pertenece al usuario
    existing = (
        admin.table("categories")
        .select("id, user_id, is_global")
        .eq("id", category_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise NotFoundError("Categoría no encontrada")

    if existing.data["is_global"]:
        raise ForbiddenError("No puedes eliminar una categoría global")

    if existing.data["user_id"] != user_id:
        raise ForbiddenError("No puedes eliminar una categoría que no es tuya")

    admin.table("categories").delete().eq("id", category_id).execute()