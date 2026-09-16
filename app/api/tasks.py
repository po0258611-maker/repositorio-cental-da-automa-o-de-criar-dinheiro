from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.core.database import SyncSessionLocal
from app.models.base import Task
from app.core.security import rate_limit
from datetime import datetime, timezone
import uuid

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    agent_name: Optional[str] = None
    project_id: Optional[str] = None
    priority: int = 5
    input_data: dict = {}

@router.get("")
def list_tasks(status: Optional[str] = None, agent_name: Optional[str] = None, limit: int = 20):
    db = SyncSessionLocal()
    try:
        q = db.query(Task).order_by(Task.created_at.desc())
        if status:
            q = q.filter(Task.status == status)
        if agent_name:
            q = q.filter(Task.agent_name == agent_name)
        tasks = q.limit(limit).all()
        return {"tasks": [{"id": t.id, "title": t.title, "status": t.status, "agent_name": t.agent_name, "priority": t.priority, "created_at": t.created_at.isoformat() if t.created_at else None} for t in tasks], "total": q.count()}
    finally:
        db.close()

@router.post("")
def create_task(req: TaskCreate, request: Request):
    rate_limit(request, limit=30)
    db = SyncSessionLocal()
    try:
        task = Task(id=str(uuid.uuid4())[:12], title=req.title, description=req.description, agent_name=req.agent_name, project_id=req.project_id, priority=req.priority, input_data=req.input_data, status="pending", created_at=datetime.now(timezone.utc))
        db.add(task)
        db.commit()
        db.refresh(task)
        return {"id": task.id, "title": task.title, "status": task.status}
    finally:
        db.close()

@router.get("/{task_id}")
def get_task(task_id: str):
    db = SyncSessionLocal()
    try:
        t = db.query(Task).filter(Task.id == task_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"id": t.id, "title": t.title, "description": t.description, "status": t.status, "agent_name": t.agent_name, "input_data": t.input_data, "output_data": t.output_data, "cost": t.cost, "error": t.error}
    finally:
        db.close()

@router.post("/{task_id}/run")
async def run_task(task_id: str, request: Request):
    rate_limit(request, limit=20)
    db = SyncSessionLocal()
    try:
        t = db.query(Task).filter(Task.id == task_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Task not found")
        t.status = "running"
        db.commit()
        # Dispatch to agent
        from app.agents import AGENTS
        agent = AGENTS.get(t.agent_name) if t.agent_name else None
        if agent:
            result = await agent.run(context=t.input_data or {})
            t.output_data = result
            t.status = "completed"
            t.completed_at = datetime.now(timezone.utc)
        else:
            t.output_data = {"mock": True, "message": f"Task {t.title} completed (no agent)"}
            t.status = "completed"
            t.completed_at = datetime.now(timezone.utc)
        db.commit()
        return {"id": t.id, "status": t.status, "output": t.output_data}
    finally:
        db.close()
