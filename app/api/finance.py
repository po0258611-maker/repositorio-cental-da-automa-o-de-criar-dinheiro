from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from app.core.economic import economic_engine
from app.core.security import rate_limit

router = APIRouter()

class TransactionCreate(BaseModel):
    amount: float
    description: str = ""
    channel: Optional[str] = "direct"
    category: Optional[str] = "operational"

@router.get("/dashboard")
def finance_dashboard():
    return economic_engine.get_dashboard()

@router.get("/transactions")
def list_transactions(limit: int = 20):
    return {"transactions": economic_engine.get_recent_transactions(limit=limit), "dashboard": economic_engine.get_dashboard()}

@router.post("/revenue")
def record_revenue(req: TransactionCreate, request: Request):
    rate_limit(request, limit=30)
    tx = economic_engine.record_revenue(req.amount, description=req.description, channel=req.channel or "direct")
    return {"transaction": tx, "dashboard": economic_engine.get_dashboard()}

@router.post("/expense")
def record_expense(req: TransactionCreate, request: Request):
    rate_limit(request, limit=30)
    tx = economic_engine.record_expense(req.amount, description=req.description, category=req.category or "operational")
    return {"transaction": tx, "dashboard": economic_engine.get_dashboard()}

@router.get("/metrics")
def metrics():
    dash = economic_engine.get_dashboard()
    return {
        "balance": dash["balance"],
        "revenue": dash["revenue"],
        "expenses": dash["expenses"],
        "profit": dash["profit"],
        "margin": dash["margin"],
        "margin_percent": dash["margin_percent"],
        "roi": dash["roi"],
        "runway_days": dash["runway_days"],
        "mode": dash["mode"],
        "cac": economic_engine.calculate_cac(200, 12),
        "ltv": economic_engine.calculate_ltv(97, 1.2, 0.7, 6),
        "roas": economic_engine.calculate_roas(dash["revenue"], 200 if dash["expenses"]>0 else 0)
    }

@router.post("/simulate")
def simulate(revenue: float = 1000, expenses: float = 300):
    # Simula cenário para decision engine
    profit = revenue - expenses
    margin = profit / revenue if revenue else 0
    return {
        "simulated": {"revenue": revenue, "expenses": expenses, "profit": profit, "margin": margin},
        "recommendation": "ESCALAR" if margin > 0.3 else "OTIMIZAR" if margin > 0 else "PAUSAR",
        "current": economic_engine.get_dashboard()
    }
