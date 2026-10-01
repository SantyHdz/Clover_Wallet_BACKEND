import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.supabase import get_supabase_admin
from app.routers import auth, categories, debts, loans, reports, savings, transactions, users

logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Clover Wallet API",
    description="Backend para la gestión financiera personal de Clover Wallet.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(debts.router)
app.include_router(loans.router)
app.include_router(reports.router)
app.include_router(savings.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Clover Wallet API", "version": "0.1.0"}


@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
def health():
    try:
        get_supabase_admin().table("categories").select("id").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception:
        logger.exception("Health check failed while connecting to database")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )