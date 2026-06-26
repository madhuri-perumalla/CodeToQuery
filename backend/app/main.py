"""Main FastAPI application."""
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.database import init_db
from app.core.errors import CodeToQueryError
from app.core.logging import setup_logging


def validate_required_secrets() -> None:
    """
    Validate that all required secrets are present and valid.

    Raises:
        SystemExit: If required secrets are missing or invalid
    """
    try:
        settings = get_settings()
        
        # Check for placeholder values
        if "CHANGE_ME" in settings.SECRET_KEY:
            print("❌ ERROR: SECRET_KEY contains placeholder value 'CHANGE_ME'")
            print("   Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
            sys.exit(1)
        
        if "CHANGE_ME" in settings.DATABASE_URL:
            print("❌ ERROR: DATABASE_URL contains placeholder value 'CHANGE_ME'")
            print("   Please set a valid DATABASE_URL in your .env file")
            sys.exit(1)
        
        if "CHANGE_ME" in settings.REDIS_URL:
            print("❌ ERROR: REDIS_URL contains placeholder value 'CHANGE_ME'")
            print("   Please set a valid REDIS_URL in your .env file")
            sys.exit(1)
        
        # Check SECRET_KEY length
        if len(settings.SECRET_KEY) < 32:
            print(f"❌ ERROR: SECRET_KEY is too short ({len(settings.SECRET_KEY)} chars, minimum 32 required)")
            print("   Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
            sys.exit(1)
        
        print("✅ All required secrets validated successfully")
        
    except ValidationError as e:
        print("❌ ERROR: Configuration validation failed")
        print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: Failed to validate configuration: {e}")
        sys.exit(1)


# Validate secrets on import
validate_required_secrets()

settings = get_settings()

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    setup_logging()
    init_db()
    yield
    # Shutdown
    pass


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CodeToQuery - Code-Aware SQL Execution Analysis Tool",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(",") if isinstance(settings.CORS_ALLOW_METHODS, str) else ["*"],
    allow_headers=settings.CORS_ALLOW_HEADERS.split(",") if isinstance(settings.CORS_ALLOW_HEADERS, str) else ["*"],
)


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Welcome to CodeToQuery API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


# Global exception handler
@app.exception_handler(CodeToQueryError)
async def codetoquery_exception_handler(request: Request, exc: CodeToQueryError) -> JSONResponse:
    """
    Handle CodeToQuery custom exceptions.

    Args:
        request: FastAPI request
        exc: CodeToQuery exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


# Global exception handler for all exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {"detail": str(exc)} if settings.DEBUG else {},
            }
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )
