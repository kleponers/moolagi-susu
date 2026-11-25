from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/")
def root_info() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "moolagi-backend",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "moolagi-backend",
        "version": settings.app_version,
        "storage_mode": settings.storage_mode,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
