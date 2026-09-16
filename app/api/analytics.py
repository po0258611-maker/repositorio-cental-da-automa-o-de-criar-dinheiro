from fastapi import APIRouter
from app.services.intelligence import intelligence_service
from app.core.memory import memory_store
from app.core.events import event_bus
from app.core.observability import metrics_store
from app.core.economic import economic_engine
from app.core.experiment import experiment_engine
from app.core.llm_router import llm_router

router = APIRouter()

@router.get("/dashboard")
async def analytics_dashboard():
    intel = await intelligence_service.analyze()
    return intel

@router.get("/kpis")
def kpis():
    return intelligence_service.get_kpis()

@router.get("/events")
def events(limit: int = 20, event_type: str = None):
    from app.core.events import EventType
    et = None
    if event_type:
        try:
            et = EventType(event_type)
        except:
            et = None
    return {"events": event_bus.history(limit=limit, event_type=et), "total": len(event_bus._history)}

@router.get("/metrics")
def metrics():
    return {
        "counters": metrics_store.counters,
        "events_count": len(metrics_store.events),
        "recent_events": metrics_store.events[-10:],
    }

@router.get("/experiments/summary")
def exp_summary():
    return experiment_engine.stats()

@router.get("/memory/summary")
def memory_summary():
    return memory_store.stats()

@router.get("/ai/costs")
def ai_costs():
    return llm_router.get_stats()

@router.get("/economic")
def economic():
    return economic_engine.get_dashboard()
