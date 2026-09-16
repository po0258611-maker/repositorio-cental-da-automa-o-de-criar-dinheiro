"""
AME - Experiment Engine
Entidade EXPERIMENT com ciclo de vida: IDEA -> VALIDATING -> BUILDING -> LIVE -> WINNER/FAILED etc.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid
from app.core.observability import logger

class ExperimentStatus(str, Enum):
    IDEA = "IDEA"
    VALIDATING = "VALIDATING"
    BUILDING = "BUILDING"
    LIVE = "LIVE"
    WINNER = "WINNER"
    OPTIMIZING = "OPTIMIZING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"

class Experiment:
    def __init__(
        self,
        name: str,
        hypothesis: str,
        product: Optional[str] = None,
        audience: Optional[str] = None,
        channel: str = "organic",
        budget: float = 0.0,
        kpi: str = "conversion",
        deadline_days: int = 14,
        risk: str = "medium",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.hypothesis = hypothesis
        self.audience = audience or "geral"
        self.product = product or "a definir"
        self.channel = channel
        self.budget = budget
        self.cost = 0.0
        self.revenue = 0.0
        self.kpi = kpi
        self.deadline = datetime.now(timezone.utc) + timedelta(days=deadline_days)
        self.risk = risk
        self.status = ExperimentStatus.IDEA
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.learnings: List[str] = []
        self.metrics: Dict[str, Any] = {}

    @property
    def profit(self) -> float:
        return self.revenue - self.cost

    @property
    def margin(self) -> float:
        if self.revenue == 0:
            return 0.0
        return self.profit / self.revenue

    @property
    def roi(self) -> float:
        if self.cost == 0:
            return 0.0
        return self.profit / self.cost

    def add_cost(self, amount: float, description: str = ""):
        self.cost += amount
        self.updated_at = datetime.now(timezone.utc)
        logger.info("experiment_cost", experiment=self.id, amount=amount, total_cost=self.cost)

    def add_revenue(self, amount: float, description: str = ""):
        self.revenue += amount
        self.updated_at = datetime.now(timezone.utc)
        logger.info("experiment_revenue", experiment=self.id, amount=amount, total_revenue=self.revenue)

    def update_metrics(self, metrics: Dict[str, Any]):
        self.metrics.update(metrics)
        self.updated_at = datetime.now(timezone.utc)

    def transition(self, new_status: ExperimentStatus, reason: str = ""):
        old = self.status
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        if reason:
            self.learnings.append(f"{datetime.now(timezone.utc).isoformat()}: {old} -> {new_status}: {reason}")
        logger.info("experiment_transition", id=self.id, old=old, new=new_status, reason=reason)
        # Eventos
        try:
            from app.core.events import emit, EventType
            if new_status == ExperimentStatus.WINNER:
                emit(EventType.ExperimentWon, {"experiment_id": self.id, "name": self.name, "profit": self.profit}, source="experiment")
            elif new_status == ExperimentStatus.FAILED:
                emit(EventType.ExperimentFailed, {"experiment_id": self.id, "name": self.name, "cost": self.cost}, source="experiment")
        except:
            pass

    def evaluate(self) -> ExperimentStatus:
        """Decision Engine - avalia se deve virar WINNER, FAILED ou continuar"""
        if self.status in [ExperimentStatus.ARCHIVED, ExperimentStatus.WINNER, ExperimentStatus.FAILED]:
            return self.status
        
        # Se passou deadline sem lucro -> FAILED
        if datetime.now(timezone.utc) > self.deadline:
            if self.profit <= 0:
                self.transition(ExperimentStatus.FAILED, "Deadline excedido sem lucro")
                return self.status
        
        # Se ROI > 2 e profit > 100 -> WINNER
        if self.roi > 2.0 and self.profit > 100:
            self.transition(ExperimentStatus.WINNER, f"ROI {self.roi:.2f} e lucro R$ {self.profit:.2f}")
            return self.status
        
        # Se custo > budget * 1.5 e sem receita -> PAUSED
        if self.cost > self.budget * 1.5 and self.revenue == 0 and self.budget > 0:
            self.transition(ExperimentStatus.PAUSED, "Custo excedeu 150% do budget sem receita")
            return self.status
        
        return self.status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "hypothesis": self.hypothesis,
            "audience": self.audience,
            "product": self.product,
            "channel": self.channel,
            "budget": self.budget,
            "cost": round(self.cost, 2),
            "revenue": round(self.revenue, 2),
            "profit": round(self.profit, 2),
            "margin": round(self.margin, 4),
            "roi": round(self.roi, 4),
            "kpi": self.kpi,
            "status": self.status.value,
            "risk": self.risk,
            "deadline": self.deadline.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metrics": self.metrics,
            "learnings": self.learnings[-5:],
            "days_remaining": (self.deadline - datetime.now(timezone.utc)).days,
        }

class ExperimentEngine:
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}

    def create(self, **kwargs) -> Experiment:
        exp = Experiment(**kwargs)
        self.experiments[exp.id] = exp
        logger.info("experiment_created", id=exp.id, name=exp.name)
        try:
            from app.core.events import emit, EventType
            emit(EventType.ExperimentCreated, {"experiment_id": exp.id, "name": exp.name}, source="experiment")
        except:
            pass
        return exp

    def get(self, exp_id: str) -> Optional[Experiment]:
        return self.experiments.get(exp_id)

    def list(self, status: Optional[str] = None) -> List[Experiment]:
        if status:
            return [e for e in self.experiments.values() if e.status.value == status]
        return list(self.experiments.values())

    def evaluate_all(self):
        for exp in self.experiments.values():
            if exp.status in [ExperimentStatus.LIVE, ExperimentStatus.VALIDATING, ExperimentStatus.BUILDING]:
                exp.evaluate()

    def stats(self) -> Dict[str, Any]:
        total = len(self.experiments)
        by_status = {}
        for s in ExperimentStatus:
            by_status[s.value] = len([e for e in self.experiments.values() if e.status == s])
        total_profit = sum(e.profit for e in self.experiments.values())
        winners = by_status.get("WINNER", 0)
        return {
            "total": total,
            "by_status": by_status,
            "total_profit": round(total_profit, 2),
            "winners": winners,
            "win_rate": round(winners / total, 4) if total else 0,
        }

# Singleton
experiment_engine = ExperimentEngine()
