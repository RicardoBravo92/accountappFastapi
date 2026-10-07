import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings, get_logger
from app.core.error_responses import create_problem_response
from app.core.exceptions import (
    DomainException,
    NotFoundError,
    ConflictError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    BusinessRuleError,
)
from app.database import Base, engine
from app.models.auth.user import RefreshToken  # Ensure audit log table is created
from app.models.auth.user import AuditLog  # Ensure audit log table is created
from app.services.rate_limit import rate_limit
from app.services.rate_limit_redis import rate_limit_manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    try:
        Base.metadata.create_all(bind=engine)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Initialize Redis rate limiter
        if settings.ENVIRONMENT != "test":
            await rate_limit_manager.initialize()
        
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {str(e)}")
    except Exception as e:
        logger.warning(f"Redis initialization failed, using in-memory fallback: {str(e)}")
        
    yield
    
    # Cleanup
    try:
        await rate_limit_manager.close()
    except Exception as e:
        logger.warning(f"Error closing Redis connection: {str(e)}")


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
    async def validate_origin_middleware(request: Request, call_next):
        """Validate Origin header for requests with credentials.
        
        This prevents CSRF by ensuring the Origin header matches
        one of the allowed CORS origins when credentials are included.
        """
        origin = request.headers.get("origin")
        if origin and request.method != "OPTIONS":
            # Allow requests without origin (e.g., mobile apps, server-to-server)
            # But if origin is present, validate it against allowed origins
            if origin not in settings.CORS_ORIGINS:
                # In development, be more permissive
                if not settings.is_development:
                    logger.warning(f"Blocked request from unallowed origin: {origin}")
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Origin not allowed"},
                    )
        response = await call_next(request)
        return response

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        """Add request ID to all requests for tracing."""
        import uuid
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Apply global rate limiting to all API requests."""
        if request.url.path.startswith("/api/"):
            rate_limit(request)
        response = await call_next(request)
        return response

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Different CSP for API vs docs
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path.startswith("/openapi.json"):
            # Permissive CSP for Swagger UI
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fastapi.tiangoli.com; "
                "img-src 'self' data: https://fastapi.tiangoli.com; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self'"
            )
        else:
            # Strict CSP for API endpoints
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        return response

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request, exc):
        logger.error(f"Database error: {exc}", exc_info=True)
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=500,
            title="Database Error",
            detail="A database operation failed",
            error_type="database-error",
        )
        return JSONResponse(status_code=500, content=problem.model_dump())

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=500,
            title="Internal Server Error",
            detail="An unexpected error occurred",
            error_type="internal-error",
        )
        return JSONResponse(status_code=500, content=problem.model_dump())

    # Domain exception handlers
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request, exc: NotFoundError):
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=status.HTTP_404_NOT_FOUND,
            title="Not Found",
            detail=exc.message,
            error_type="not-found",
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=problem.model_dump())

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(request, exc: ConflictError):
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=status.HTTP_409_CONFLICT,
            title="Conflict",
            detail=exc.message,
            error_type="conflict",
        )
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=problem.model_dump())

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc: ValidationError):
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Error",
            detail=exc.message,
            error_type="validation-error",
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=problem.model_dump())

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_exception_handler(request, exc: UnauthorizedError):
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Unauthorized",
            detail=exc.message,
            error_type="unauthorized",
        )
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=problem.model_dump())

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(request, exc: ForbiddenError):
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=status.HTTP_403_FORBIDDEN,
            title="Forbidden",
            detail=exc.message,
            error_type="forbidden",
        )
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=problem.model_dump())

    @app.exception_handler(BusinessRuleError)
    async def business_rule_exception_handler(request, exc: BusinessRuleError):
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Business Rule Violation",
            detail=exc.message,
            error_type="business-rule-violation",
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=problem.model_dump())

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request, exc: DomainException):
        """Catch-all for any unhandled domain exceptions."""
        logger.warning(f"Domain exception: {exc.code} - {exc.message}")
        problem = create_problem_response(
            request_path=str(request.url),
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Bad Request",
            detail=exc.message,
            error_type="bad-request",
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=problem.model_dump())

    # API v1 routers
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health")
    async def health_check():
        """Health check endpoint with actual database connectivity test."""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "connected"
            overall_status = "ok"
        except Exception:
            db_status = "disconnected"
            overall_status = "degraded"

        return {
            "status": overall_status,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": db_status,
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
