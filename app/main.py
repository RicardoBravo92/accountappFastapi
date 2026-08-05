import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings, get_logger
from app.database import Base, engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    try:
        Base.metadata.create_all(bind=engine)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {str(e)}")
        
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "authentication",
                "description": "User authentication and authorization operations",
            },
            {
                "name": "accounts",
                "description": "Account management and operations",
            },
            {
                "name": "transactions",
                "description": "Financial transaction management",
            },
            {
                "name": "reports",
                "description": "Financial reporting and analytics",
            },
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Allow Swagger UI resources
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fastapi.tiangoli.com; "
            "img-src 'self' data: https://fastapi.tiangoli.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'"
        )
        return response

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database error",
                "message": str(exc),
                "detail": "A database operation failed",
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc),
                "detail": "An unexpected error occurred",
            },
        )

    # API v1 routers
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "connected" if engine else "disconnected",
        }

    @app.get("/")
    async def root():
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Welcome to {settings.APP_NAME} API",
                "version": settings.APP_VERSION,
                "docs_url": "/docs",
                "redoc_url": "/redoc",
                "health_check": "/health",
                "status": "running",
            },
        )

    return app


app = create_app()
