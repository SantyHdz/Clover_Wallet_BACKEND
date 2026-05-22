from functools import lru_cache
from supabase import create_client, Client
from app.config import get_settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """
    Cliente de Supabase con la ANON KEY.
    Se usa para operaciones autenticadas con el JWT del usuario.
    RLS activo — cada usuario solo ve sus datos.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


@lru_cache(maxsize=1)
def get_supabase_admin() -> Client:
    """
    Cliente de Supabase con la SERVICE ROLE KEY.
    Bypasea RLS. Solo usar en operaciones administrativas
    como crear usuarios, subir avatares o queries de reporte
    que cruzan datos de sistema.
    NUNCA exponer este cliente en endpoints públicos.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)