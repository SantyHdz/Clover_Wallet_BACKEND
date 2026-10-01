import logging
from gotrue.errors import AuthApiError

from app.core.exceptions import ConflictError, InternalServerError, UnauthorizedError
from app.core.security import create_access_token
from app.core.supabase import get_auth_client, get_supabase_admin
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

logger = logging.getLogger(__name__)


def register_user(data: RegisterRequest) -> TokenResponse:
    admin = get_supabase_admin()

    try:
        response = admin.auth.admin.create_user({
            "email": data.email,
            "password": data.password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": data.full_name,
                "provider": "email",
            },
        })
    except AuthApiError as e:
        msg = str(e).lower()
        if "already" in msg or "exists" in msg or "registered" in msg:
            raise ConflictError("Ya existe una cuenta con ese email")
        logger.exception("Error inesperado de Supabase Auth al registrar usuario: %s", e)
        raise InternalServerError("Error al crear el usuario en el servicio de autenticación")
    except Exception as e:
        logger.exception("Error inesperado en register_user: %s", e)
        raise InternalServerError("Error interno al procesar el registro")

    user = response.user if hasattr(response, "user") else response
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)


def login_user(data: LoginRequest) -> TokenResponse:
    auth_client = get_auth_client()

    try:
        response = auth_client.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except AuthApiError:
        raise UnauthorizedError("Credenciales incorrectas")

    user = response.user
    if not user:
        raise UnauthorizedError("Credenciales incorrectas")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)

def login_google_user(payload: dict) -> TokenResponse:
    """
    El usuario ya fue validado por get_current_user con el token de Supabase.
    Solo emitimos nuestro JWT propio.
    """
    user_id = payload.get("sub")
    email = payload.get("email", "")
    token = create_access_token({"sub": str(user_id), "email": email})
    return TokenResponse(access_token=token)




