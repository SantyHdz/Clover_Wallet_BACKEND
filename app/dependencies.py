from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Dependencia reutilizable en cualquier endpoint protegido.

    Uso en un router:
        @router.get("/me")
        async def get_me(user: dict = Depends(get_current_user)):
            return user

    Retorna el payload del JWT con al menos:
        - sub  : UUID del usuario (su id en auth.users / profiles)
        - email: email del usuario
        - exp  : timestamp de expiración
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise UnauthorizedError("Token inválido o expirado")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Token sin identificador de usuario")

    return payload