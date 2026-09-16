"""
AME - Economic Engine
Camada financeira: PROFIT, MARGIN, ROI, RUNWAY, BALANCE, BURN, CAC, LTV, ROAS
Monitora permanentemente e define modo: GROW, NORMAL, SURVIVAL, EMERGENCY
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
from sqlalchemy.orm import Session
from app.core.observability import logger

class SurvivalMode(str, Enum):
    GROW = "GROW"           # gerando valor consistentemente
    NORMAL = "NORMAL"       # equilibrado
    SURVIVAL = "SURVIVAL"   # receita insuficiente
    EMERGENCY = "EMERGENCY" # risco elevado

class EconomicEngine:
    def __init__(self, initial_balance: float = 1000.0, burn_rate_daily: float = 5.0):
        self.balance = initial_balance
        self.burn_rate_daily = burn_rate_daily
        self.revenue_total = 0.0
        self.expenses_total = 0.0
        self.transactions: List[Dict[str, Any]] = []
        self.mode = SurvivalMode.NORMAL
        self.survival_threshold_days = 7
        self.emergency_threshold_days = 3

    def record_revenue(self, amount: float, description: str = "Revenue", channel: str = "direct", metadata: Optional[Dict] = None) -> Dict[str, Any]:
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
        self.transactions.append(tx)
        logger.info("revenue_recorded", amount=amount, channel=channel, balance=self.balance)
        self._update_mode()
        # metrics
        try:
            from app.core.observability import REVENUE_GAUGE, PROFIT_GAUGE
            REVENUE_GAUGE.set(self.revenue_total)
            PROFIT_GAUGE.set(self.profit)
        except:
            pass
        # evento
        try:
            from app.core.events import emit, EventType
            emit(EventType.RevenueReceived, {"amount": amount, "channel": channel, "balance": self.balance}, source="economic")
        except:
            pass
        return tx

    def record_expense(self, amount: float, description: str = "Expense", category: str = "operational", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        self.expenses_total += amount
        self.balance -= amount
        if self.balance < 0:
            self.balance = 0
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
        self.transactions.append(tx)
        logger.info("expense_recorded", amount=amount, category=category, balance=self.balance)
        self._update_mode()
        try:
            from app.core.observability import PROFIT_GAUGE
            PROFIT_GAUGE.set(self.profit)
        except:
            pass
        try:
            from app.core.events import emit, EventType
            emit(EventType.ExpenseRecorded, {"amount": amount, "category": category, "balance": self.balance}, source="economic")
        except:
            pass
        return tx

    @property
    def profit(self) -> float:
        return self.revenue_total - self.expenses_total

    @property
    def margin(self) -> float:
        if self.revenue_total == 0:
            return 0.0
        return self.profit / self.revenue_total

    def roi(self, investment: float) -> float:
        if investment == 0:
            return 0.0
        return self.profit / investment

    @property
    def runway_days(self) -> float:
        if self.burn_rate_daily <= 0:
            return 9999
        return self.balance / self.burn_rate_daily

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
            logger.warning("survival_mode_changed", old=old_mode, new=self.mode, runway=runway, balance=self.balance)
            # Ações automáticas por modo
            if self.mode == SurvivalMode.EMERGENCY:
                logger.error("emergency_mode_activated", message="Interrompendo operações não essenciais, preservando caixa")
            elif self.mode == SurvivalMode.SURVIVAL:
                logger.warning("survival_mode_activated", message="Reduzindo chamadas caras, priorizando produtos vencedores")

    def calculate_cac(self, marketing_spend: float, new_customers: int) -> float:
        if new_customers == 0:
            return 0.0
        return marketing_spend / new_customers

    def calculate_ltv(self, avg_purchase_value: float, purchase_frequency: float, gross_margin: float, avg_customer_lifespan_months: float) -> float:
        return avg_purchase_value * purchase_frequency * gross_margin * avg_customer_lifespan_months

    def calculate_roas(self, revenue: float, ad_spend: float) -> float:
        if ad_spend == 0:
            return 0.0
        return revenue / ad_spend

    def get_dashboard(self) -> Dict[str, Any]:
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
        """Decision Engine helper - verifica se operação cara pode ser feita dado modo atual"""
        if self.mode == SurvivalMode.EMERGENCY:
            return cost < 0.10  # só operações muito baratas
        if self.mode == SurvivalMode.SURVIVAL:
            return cost < 1.0
        return True

    def get_recent_transactions(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.transactions[-limit:]

# Singleton global - inicializado com settings
from app.core.config import settings
economic_engine = EconomicEngine(initial_balance=settings.initial_balance, burn_rate_daily=settings.burn_rate_daily)
economic_engine.survival_threshold_days = settings.survival_threshold_days
economic_engine.emergency_threshold_days = settings.emergency_threshold_days
