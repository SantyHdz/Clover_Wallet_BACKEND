from app.core.exceptions import NotFoundError
from app.core.supabase import get_supabase_admin
from app.schemas.users import ProfileResponse, UpdateProfileRequest


def get_profile(user_id: str) -> ProfileResponse:
    admin = get_supabase_admin()

    result = (
        admin.table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )

    if not result.data:
        raise NotFoundError("Perfil no encontrado")

    return ProfileResponse(**result.data)


def update_profile(user_id: str, data: UpdateProfileRequest) -> ProfileResponse:
    admin = get_supabase_admin()

    # Solo enviar campos que el usuario realmente mandó
    payload = data.model_dump(exclude_none=True)
    if not payload:
        return get_profile(user_id)

    result = (
        admin.table("profiles")
        .update(payload)
        .eq("id", user_id)
        .execute()
    )

    if not result.data:
        raise NotFoundError("Perfil no encontrado")

    return ProfileResponse(**result.data[0])


def update_avatar(user_id: str, avatar_url: str) -> ProfileResponse:
    admin = get_supabase_admin()

    result = (
        admin.table("profiles")
        .update({"avatar_url": avatar_url})
        .eq("id", user_id)
        .execute()
    )

    if not result.data:
        raise NotFoundError("Perfil no encontrado")

    return ProfileResponse(**result.data[0])


def upload_avatar_to_storage(user_id: str, file_bytes: bytes, content_type: str) -> str:
    """
    Sube la imagen al bucket 'avatars' de Supabase Storage.
    Retorna la URL pública del archivo subido.
    El archivo se guarda como avatars/{user_id} sobreescribiendo el anterior.
    """
    admin = get_supabase_admin()
    path = f"{user_id}"

    # upsert=True sobreescribe si ya existe
    admin.storage.from_("avatars").upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": content_type, "upsert": "true"},
    )

    public_url = admin.storage.from_("avatars").get_public_url(path)
    return public_url