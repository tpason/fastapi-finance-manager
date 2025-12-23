from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router

# Import models để đăng ký vào Base.metadata
# Quan trọng: Phải import trước khi gọi create_all()
from app.models import User, Transaction, Category, UserDeviceToken, UserCategory  # noqa: F401

# Create database tables (only if database is available)
# Note: This will fail if database is not accessible, but that's okay for startup
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
except Exception:
    # Database connection will be checked when endpoints are called
    pass

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Financial Management API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
