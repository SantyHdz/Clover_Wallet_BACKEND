from fastapi import APIRouter, Depends, Header
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services import auth as auth_service
from app.dependencies import get_current_user
from app.core.security import decode_supabase_token
from app.core.exceptions import UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest):
    return auth_service.register_user(data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    return auth_service.login_user(data)


@router.post("/login/google", response_model=TokenResponse)
def login_google(authorization: str = Header(...)):
    """
    Recibe el token de Supabase (emitido al autenticar con Google),
    extrae el sub y email, y emite nuestro propio JWT del backend.
    """
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("Token inválido")
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_supabase_token(token)
    except Exception:
        raise UnauthorizedError("Token de Supabase inválido")
    return auth_service.login_google_user(payload)