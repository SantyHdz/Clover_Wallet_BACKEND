from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Contraseñas ────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ────────────────────────────────────────────────────────────────────────

def create_access_token(data: dict[str, Any]) -> str:
    settings = get_settings()
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decodifica y valida el JWT.
    Lanza JWTError si el token es inválido o expiró.
    El router no llama esto directamente — lo hace dependencies.py.
    """
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

def decode_supabase_token(token: str) -> dict:
    """
    Decodifica un JWT de Supabase sin verificar firma
    (la verificación ya la hizo Supabase al emitirlo).
    Solo extraemos el payload para obtener sub y email.
    """
    import base64, json
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Token inválido")
    padding = 4 - len(parts[1]) % 4
    payload_bytes = base64.urlsafe_b64decode(parts[1] + "=" * padding)
    return json.loads(payload_bytes)