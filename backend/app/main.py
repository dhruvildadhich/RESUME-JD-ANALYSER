"""
FastAPI Application Factory.

- Configures structured logging at startup
- Pre-warms the SentenceTransformer model (avoids cold start on first request)
- Mounts CORS middleware
- Registers the analysis router
- Adds a global exception handler for clean error responses
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config.settings import get_settings
from app.core.cache import initialize_cache
from app.core.logging import get_logger, setup_logging
from app.services.embedding_service import EmbeddingService

settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Pre-warm expensive resources on startup."""
    logger.info("Starting Resume-JD Matcher API")
    initialize_cache()
    try:
        await EmbeddingService.warmup()  # load model into memory before first request
        logger.info("Embedding model pre-warmed successfully")
    except Exception as exc:
        logger.warning("Embedding model pre-warm failed", extra={"error": str(exc)})
    yield
    logger.info("Shutting down Resume-JD Matcher API")


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="Resume–JD Matcher API",
        description=(
            "AI-powered tool that compares a candidate resume against a job description, "
            "extracts skills, calculates a hybrid match score, and generates improvement suggestions."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(set(settings.cors_origins + [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ])),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(router)

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            extra={"path": str(request.url), "error": str(exc)},
        )
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "message": "An unexpected error occurred."},
        )

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health() -> dict:
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()
