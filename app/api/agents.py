from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from app.core.security import rate_limit
from app.agents import AGENTS
from app.core.orchestrator import orchestrator
from pydantic import BaseModel

router = APIRouter()

class AgentRunRequest(BaseModel):
    context: dict = {}

@router.get("")
def list_agents(category: Optional[str] = None):
    agents = []
    for name, agent in AGENTS.items():
        if category and agent.category != category.upper():
            continue
        agents.append(agent.to_dict())
    return {"agents": agents, "total": len(agents), "categories": list(set(a.category for a in AGENTS.values()))}

@router.get("/{agent_name}")
def get_agent(agent_name: str):
    agent = AGENTS.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    return agent.to_dict()

@router.post("/{agent_name}/run")
async def run_agent(agent_name: str, req: AgentRunRequest, request: Request):
    rate_limit(request, limit=20)
    agent = AGENTS.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    result = await agent.run(context=req.context)
    return {"agent": agent_name, "result": result}

@router.post("/orchestrator/cycle")
async def run_orchestrator_cycle(request: Request):
    rate_limit(request, limit=10)
    result = await orchestrator.run_cycle()
    return result

@router.get("/orchestrator/status")
def orchestrator_status():
    return orchestrator.get_status()

@router.post("/orchestrator/pause")
def orchestrator_pause():
    orchestrator.pause()
    return {"paused": True}

@router.post("/orchestrator/resume")
def orchestrator_resume():
    orchestrator.resume()
    return {"paused": False}

@router.post("/orchestrator/stop")
def orchestrator_stop():
    orchestrator.stop()
    return {"running": False}
