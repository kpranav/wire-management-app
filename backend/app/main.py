"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.routers import auth_router, wires_router
from app.routers.websocket import router as websocket_router
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.utils.redis_client import cache
from fastapi import HTTPException

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth_router)
app.include_router(wires_router)
app.include_router(websocket_router)


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    try:
        await cache.connect()
        print("✅ Redis cache connected")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        await cache.disconnect()
        print("Redis cache disconnected")
    except Exception:
        pass


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Wire Management API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
