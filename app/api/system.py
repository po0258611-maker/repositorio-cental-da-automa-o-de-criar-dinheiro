from fastapi import APIRouter
from app.core.orchestrator import orchestrator
from app.core.database import sync_engine
from sqlalchemy import text
from datetime import datetime, timezone
import os
import platform
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

router = APIRouter()

@router.get("/status")
def system_status():
    orch = orchestrator.get_status()
    db_ok = True
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except:
        db_ok = False
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "orchestrator": orch,
        "database": "up" if db_ok else "down",
        "env": os.getenv("AME_ENV", "development"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu_percent": psutil.cpu_percent(interval=0.1) if HAS_PSUTIL else 0,
    }

@router.get("/tasks")
def list_tasks(limit: int = 20):
    # tasks from orchestrator
    return {"completed": orchestrator.completed_tasks[-limit:], "queue": orchestrator.tasks_queue, "total_completed": len(orchestrator.completed_tasks)}

@router.post("/loop/start")
async def start_loop(interval: int = 60, max_cycles: int = 1):
    # Run one cycle for demo
    result = await orchestrator.run_cycle()
    return {"started": True, "result": result}

@router.get("/loop/history")
def loop_history(limit: int = 10):
    return {"history": orchestrator.completed_tasks[-limit:], "total": len(orchestrator.completed_tasks)}

@router.get("/config")
def get_config():
    from app.core.config import settings
    # Mask secrets
    return {
        "ame_env": settings.ame_env,
        "database_url": settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url,
        "max_daily_ai_cost": settings.max_daily_ai_cost_usd,
        "initial_balance": settings.initial_balance,
        "survival_threshold_days": settings.survival_threshold_days,
        "emergency_threshold_days": settings.emergency_threshold_days,
        "cors_origins": settings.cors_origins,
    }
