"""
AME - Economic Engine
Persistent economic state backed by the Transaction table.
The in-memory values are a cache; the database is the source of truth.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid

from app.core.observability import logger
from app.core.database import SyncSessionLocal
from app.models.base import Transaction
from app.core.config import settings


class SurvivalMode(str, Enum):
    GROW = "GROW"
    NORMAL = "NORMAL"
    SURVIVAL = "SURVIVAL"
    EMERGENCY = "EMERGENCY"


class EconomicEngine:
    def __init__(self, initial_balance: float = 1000.0, burn_rate_daily: float = 5.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.burn_rate_daily = burn_rate_daily
        self.revenue_total = 0.0
        self.expenses_total = 0.0
        self.transactions: List[Dict[str, Any]] = []
        self.mode = SurvivalMode.NORMAL
        self.survival_threshold_days = 7
        self.emergency_threshold_days = 3
        self._hydrate()

    def _hydrate(self) -> None:
        try:
            db = SyncSessionLocal()
            try:
                rows = db.query(Transaction).order_by(Transaction.created_at.asc()).all()
                self.revenue_total = sum(float(t.amount) for t in rows if t.type == "revenue")
                self.expenses_total = sum(float(t.amount) for t in rows if t.type == "expense")
                self.balance = self.initial_balance + self.revenue_total - self.expenses_total
                self.transactions = [
                    {
                        "id": t.id,
                        "type": t.type,
                        "amount": float(t.amount),
                        "description": t.description,
                        "category": t.category,
                        "channel": t.channel,
                        "metadata": t.extra_data or {},
                        "timestamp": t.created_at.isoformat() if t.created_at else None,
                        "balance_after": float(t.balance_after) if t.balance_after is not None else None,
                    }
                    for t in rows[-500:]
                ]
            finally:
                db.close()
            self._update_mode()
        except Exception as exc:
            logger.warning("economic_hydrate_skipped", error=str(exc))

    def _persist(self, tx: Dict[str, Any]) -> None:
        db = SyncSessionLocal()
        try:
            row = Transaction(
                id=tx["id"],
                type=tx["type"],
                amount=tx["amount"],
                description=tx.get("description"),
                category=tx.get("category"),
                channel=tx.get("channel"),
                balance_after=tx.get("balance_after"),
                extra_data=tx.get("metadata") or {},
                created_at=datetime.fromisoformat(tx["timestamp"]),
            )
            db.add(row)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def record_revenue(self, amount: float, description: str = "Revenue", channel: str = "direct", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        if amount < 0:
            raise ValueError("Revenue amount must be non-negative")
        self.revenue_total += amount
        self.balance += amount
        tx = {
            "id": str(uuid.uuid4()),
            "type": "revenue",
            "amount": amount,
            "description": description,
            "channel": channel,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "balance_after": self.balance,
        }
        try:
            self._persist(tx)
        except Exception:
            self.revenue_total -= amount
            self.balance -= amount
            raise
        self.transactions.append(tx)
        self.transactions = self.transactions[-500:]
        self._update_mode()
        self._emit_financial_metrics("revenue")
        return tx

    def record_expense(self, amount: float, description: str = "Expense", category: str = "operational", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        if amount < 0:
            raise ValueError("Expense amount must be non-negative")
        self.expenses_total += amount
        self.balance -= amount
        tx = {
            "id": str(uuid.uuid4()),
            "type": "expense",
            "amount": amount,
            "description": description,
            "category": category,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "balance_after": self.balance,
        }
        try:
            self._persist(tx)
        except Exception:
            self.expenses_total -= amount
            self.balance += amount
            raise
        self.transactions.append(tx)
        self.transactions = self.transactions[-500:]
        self._update_mode()
        self._emit_financial_metrics("expense")
        return tx

    @property
    def profit(self) -> float:
        return self.revenue_total - self.expenses_total

    @property
    def margin(self) -> float:
        return self.profit / self.revenue_total if self.revenue_total else 0.0

    def roi(self, investment: float) -> float:
        return self.profit / investment if investment else 0.0

    @property
    def runway_days(self) -> float:
        return 9999 if self.burn_rate_daily <= 0 else max(0.0, self.balance / self.burn_rate_daily)

    @property
    def burn_rate(self) -> float:
        return self.burn_rate_daily

    def _update_mode(self):
        runway = self.runway_days
        old_mode = self.mode
        if runway <= self.emergency_threshold_days:
            self.mode = SurvivalMode.EMERGENCY
        elif runway <= self.survival_threshold_days:
            self.mode = SurvivalMode.SURVIVAL
        elif self.profit > 0 and self.margin > 0.3:
            self.mode = SurvivalMode.GROW
        else:
            self.mode = SurvivalMode.NORMAL
        if old_mode != self.mode:
            logger.warning("survival_mode_changed", old=old_mode.value, new=self.mode.value, runway=runway)

    def calculate_cac(self, marketing_spend: float, new_customers: int) -> float:
        return marketing_spend / new_customers if new_customers else 0.0

    def calculate_ltv(self, avg_purchase_value: float, purchase_frequency: float, gross_margin: float, avg_customer_lifespan_months: float) -> float:
        return avg_purchase_value * purchase_frequency * gross_margin * avg_customer_lifespan_months

    def calculate_roas(self, revenue: float, ad_spend: float) -> float:
        return revenue / ad_spend if ad_spend else 0.0

    def _emit_financial_metrics(self, event_kind: str) -> None:
        try:
            from app.core.observability import REVENUE_GAUGE, PROFIT_GAUGE
            REVENUE_GAUGE.set(self.revenue_total)
            PROFIT_GAUGE.set(self.profit)
        except Exception:
            pass
        try:
            from app.core.events import emit, EventType
            event = EventType.RevenueReceived if event_kind == "revenue" else EventType.ExpenseRecorded
            emit(event, {"amount": self.transactions[-1]["amount"], "balance": self.balance}, source="economic")
        except Exception:
            pass

    def get_dashboard(self) -> Dict[str, Any]:
        # Refresh persisted truth before reporting.
        self._hydrate()
        return {
            "balance": round(self.balance, 2),
            "revenue": round(self.revenue_total, 2),
            "expenses": round(self.expenses_total, 2),
            "profit": round(self.profit, 2),
            "margin": round(self.margin, 4),
            "margin_percent": round(self.margin * 100, 2),
            "runway_days": round(self.runway_days, 1),
            "burn_rate_daily": self.burn_rate_daily,
            "mode": self.mode.value,
            "roi": round(self.roi(self.expenses_total) if self.expenses_total else 0, 4),
            "transactions_count": len(self.transactions),
        }

    def should_allow_expensive_operation(self, cost: float) -> bool:
        if self.mode == SurvivalMode.EMERGENCY:
            return cost < 0.10
        if self.mode == SurvivalMode.SURVIVAL:
            return cost < 1.0
        return True

    def get_recent_transactions(self, limit: int = 20) -> List[Dict[str, Any]]:
        db = SyncSessionLocal()
        try:
            rows = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(max(1, min(limit, 200))).all()
            return [
                {
                    "id": t.id,
                    "type": t.type,
                    "amount": float(t.amount),
                    "description": t.description,
                    "category": t.category,
                    "channel": t.channel,
                    "metadata": t.extra_data or {},
                    "timestamp": t.created_at.isoformat() if t.created_at else None,
                    "balance_after": float(t.balance_after) if t.balance_after is not None else None,
                }
                for t in rows
            ]
        finally:
            db.close()


economic_engine = EconomicEngine(
    initial_balance=settings.initial_balance,
    burn_rate_daily=settings.burn_rate_daily,
)
economic_engine.survival_threshold_days = settings.survival_threshold_days
economic_engine.emergency_threshold_days = settings.emergency_threshold_days
