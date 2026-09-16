from fastapi import APIRouter, Depends
from app.core.observability import get_health_status, logger
from app.core.database import sync_engine
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
def health():
    db_ok = True
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("health_db_failed", error=str(e))
        db_ok = False
    return get_health_status(db_ok=db_ok)

@router.get("/ready")
def ready():
    return {"ready": True}

@router.get("/live")
def live():
    return {"live": True}
