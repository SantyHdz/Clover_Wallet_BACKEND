from gotrue.errors import AuthApiError

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token
from app.core.supabase import get_supabase_admin
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


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
        raise ConflictError(f"Error al crear el usuario: {e}")

    user = response.user if hasattr(response, "user") else response
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)


def login_user(data: LoginRequest) -> TokenResponse:
    admin = get_supabase_admin()

    try:
        response = admin.auth.sign_in_with_password({
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




