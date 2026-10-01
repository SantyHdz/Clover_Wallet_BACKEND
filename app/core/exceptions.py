from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


# ── Excepciones personalizadas ─────────────────────────────────────────────────

class NotFoundError(Exception):
    def __init__(self, detail: str = "Recurso no encontrado"):
        self.detail = detail


class UnauthorizedError(Exception):
    def __init__(self, detail: str = "No autorizado"):
        self.detail = detail


class ForbiddenError(Exception):
    def __init__(self, detail: str = "Acceso denegado"):
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str = "Conflicto con el estado actual del recurso"):
        self.detail = detail


class BadRequestError(Exception):
    def __init__(self, detail: str = "Solicitud inválida"):
        self.detail = detail


class InternalServerError(Exception):
    def __init__(self, detail: str = "Error interno del servidor"):
        self.detail = detail


# ── Registro de handlers en la app ─────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.detail},
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.detail},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.detail},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.detail},
        )

    @app.exception_handler(BadRequestError)
    async def bad_request_handler(request: Request, exc: BadRequestError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail},
        )

    @app.exception_handler(InternalServerError)
    async def internal_server_error_handler(request: Request, exc: InternalServerError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": exc.detail},
        )