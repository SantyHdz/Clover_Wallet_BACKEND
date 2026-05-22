from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.routers import auth, categories, debts, loans, reports, transactions, users

settings = get_settings()

app = FastAPI(
    title="Clover Wallet API",
    description="Backend para la gestión financiera personal de Clover Wallet.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Handlers de error globales ─────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(debts.router)
app.include_router(loans.router)
app.include_router(reports.router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Clover Wallet API", "version": "0.1.0"}