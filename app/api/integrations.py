from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.core.database import SyncSessionLocal
from app.models.base import Integration
from app.core.security import rate_limit
from datetime import datetime, timezone
import uuid

router = APIRouter()

class IntegrationCreate(BaseModel):
    name: str
    type: str
    is_active: bool = False
    config: dict = {}

@router.get("")
def list_integrations():
    db = SyncSessionLocal()
    try:
        ints = db.query(Integration).all()
        return {"integrations": [{"name": i.name, "type": i.type, "is_active": i.is_active, "last_sync": i.last_sync.isoformat() if i.last_sync else None} for i in ints], "total": len(ints)}
    finally:
        db.close()

@router.post("")
def create_integration(req: IntegrationCreate, request: Request):
    rate_limit(request, limit=20)
    db = SyncSessionLocal()
    try:
        existing = db.query(Integration).filter(Integration.name == req.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Integration already exists")
        integ = Integration(id=str(uuid.uuid4())[:12], name=req.name, type=req.type, is_active=req.is_active, config=req.config, created_at=datetime.now(timezone.utc))
        db.add(integ)
        db.commit()
        return {"name": integ.name, "type": integ.type, "is_active": integ.is_active}
    finally:
        db.close()

@router.post("/{name}/toggle")
def toggle_integration(name: str):
    db = SyncSessionLocal()
    try:
        integ = db.query(Integration).filter(Integration.name == name).first()
        if not integ:
            raise HTTPException(status_code=404, detail="Integration not found")
        integ.is_active = not integ.is_active
        integ.last_sync = datetime.now(timezone.utc)
        db.commit()
        return {"name": integ.name, "is_active": integ.is_active}
    finally:
        db.close()

@router.get("/tools")
def list_tools():
    from app.core.tools import tool_registry
    tools = tool_registry.list()
    return {"tools": [{"name": t.name, "description": t.description, "cost": t.cost, "risk": t.risk.value, "timeout": t.timeout, "retry": t.retry} for t in tools], "total": len(tools)}

@router.post("/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, payload: dict, request: Request):
    rate_limit(request, limit=20)
    from app.core.tools import tool_registry
    tool = tool_registry.get(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    result = await tool_registry.execute(tool_name, **payload)
    return result
