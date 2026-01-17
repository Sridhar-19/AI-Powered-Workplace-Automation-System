"""
Health check endpoints
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    environment: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check with service statuses"""
    status: str
    version: str
    environment: str
    services: Dict[str, Any]


@router.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint
    Returns simple status of the application
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.env
    )


@router.get("/readiness", response_model=DetailedHealthResponse)
async def readiness_check():
    """
    Readiness check - verifies all dependencies are available
    Checks connections to external services (OpenAI, Pinecone, etc.)
    """
    services_status = {}
    overall_healthy = True
    
    # Check OpenAI configuration
    try:
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            services_status["openai"] = {"status": "configured", "model": settings.openai_model}
        else:
            services_status["openai"] = {"status": "not_configured"}
            overall_healthy = False
    except Exception as e:
        services_status["openai"] = {"status": "error", "message": str(e)}
        overall_healthy = False
    
    # Check Pinecone configuration
    try:
        if settings.pinecone_api_key and settings.pinecone_api_key != "your_pinecone_api_key_here":
            services_status["pinecone"] = {
                "status": "configured",
                "index": settings.pinecone_index_name,
                "environment": settings.pinecone_environment
            }
        else:
            services_status["pinecone"] = {"status": "not_configured"}
            overall_healthy = False
    except Exception as e:
        services_status["pinecone"] = {"status": "error", "message": str(e)}
        overall_healthy = False
    
    # Check Teams bot configuration (optional)
    if settings.microsoft_app_id and settings.microsoft_app_id != "your_azure_app_id_here":
        services_status["teams_bot"] = {"status": "configured"}
    else:
        services_status["teams_bot"] = {"status": "not_configured", "note": "optional"}
    
    return DetailedHealthResponse(
        status="healthy" if overall_healthy else "degraded",
        version="1.0.0",
        environment=settings.env,
        services=services_status
    )


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check - verifies application is running
    Simple check that returns 200 if application is alive
    """
    return {"status": "alive"}
