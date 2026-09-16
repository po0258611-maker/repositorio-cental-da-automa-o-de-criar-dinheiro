from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.memory import memory_store
from app.core.security import rate_limit

router = APIRouter()

class MemoryCreate(BaseModel):
    category: str
    action: str
    result: str
    cost: float = 0.0
    lesson: str = ""
    next_action: str = ""
    metric: dict = {}
    metadata: dict = {}

@router.get("")
def list_memory(category: Optional[str] = None, limit: int = 20, contains: Optional[str] = None):
    return {"memories": memory_store.query(category=category, limit=limit, contains=contains), "stats": memory_store.stats()}

@router.post("")
def add_memory(req: MemoryCreate, request: Request):
    rate_limit(request, limit=50)
    try:
        entry = memory_store.add(category=req.category, action=req.action, result=req.result, cost=req.cost, lesson=req.lesson, next_action=req.next_action, metric=req.metric, metadata=req.metadata)
        return entry.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/failures")
def failures(limit: int = 10):
    return {"failures": memory_store.get_failures(limit=limit)}

@router.get("/successes")
def successes(limit: int = 10):
    return {"successes": memory_store.get_successes(limit=limit)}

@router.get("/stats")
def stats():
    return memory_store.stats()

@router.get("/should-avoid")
def should_avoid(action: str):
    return {"action": action, "should_avoid": memory_store.should_avoid(action)}
