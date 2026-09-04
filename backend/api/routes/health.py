"""
settle — Health Check Route

Simple endpoint to verify the API is running.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Return API health status."""
    return {
        "status": "healthy",
        "service": "settle API",
        "version": "0.2.0",
    }
