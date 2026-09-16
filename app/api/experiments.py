from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.core.experiment import experiment_engine, ExperimentStatus
from app.core.security import rate_limit

router = APIRouter()

class ExperimentCreate(BaseModel):
    name: str
    hypothesis: str
    product: Optional[str] = None
    audience: Optional[str] = None
    channel: str = "organic"
    budget: float = 0.0
    kpi: str = "conversion"
    deadline_days: int = 14
    risk: str = "medium"

class ExperimentUpdate(BaseModel):
    status: Optional[str] = None
    cost: Optional[float] = None
    revenue: Optional[float] = None
    metrics: Optional[dict] = None

@router.get("")
def list_experiments(status: Optional[str] = None):
    exps = experiment_engine.list(status=status)
    return {"experiments": [e.to_dict() for e in exps], "stats": experiment_engine.stats()}

@router.get("/stats")
def stats():
    return experiment_engine.stats()

@router.post("")
def create_experiment(req: ExperimentCreate, request: Request):
    rate_limit(request, limit=30)
    exp = experiment_engine.create(
        name=req.name,
        hypothesis=req.hypothesis,
        product=req.product,
        audience=req.audience,
        channel=req.channel,
        budget=req.budget,
        kpi=req.kpi,
        deadline_days=req.deadline_days,
        risk=req.risk
    )
    return exp.to_dict()

@router.get("/{exp_id}")
def get_experiment(exp_id: str):
    exp = experiment_engine.get(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp.to_dict()

@router.patch("/{exp_id}")
def update_experiment(exp_id: str, req: ExperimentUpdate):
    exp = experiment_engine.get(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if req.status:
        try:
            exp.transition(ExperimentStatus(req.status), reason="API update")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status {req.status}")
    if req.cost is not None:
        exp.add_cost(req.cost)
    if req.revenue is not None:
        exp.add_revenue(req.revenue)
    if req.metrics:
        exp.update_metrics(req.metrics)
    exp.evaluate()
    return exp.to_dict()

@router.post("/{exp_id}/evaluate")
def evaluate_experiment(exp_id: str):
    exp = experiment_engine.get(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    old = exp.status
    new = exp.evaluate()
    return {"id": exp_id, "old_status": old.value, "new_status": new.value, "experiment": exp.to_dict()}

@router.post("/evaluate-all")
def evaluate_all():
    experiment_engine.evaluate_all()
    return experiment_engine.stats()
