"""
AME - Observability
Logs estruturados, métricas, health, tracing básico
"""
import time
import logging
import structlog
from typing import Dict, Any
from datetime import datetime, timezone
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Structlog config
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if not __import__("os").environ.get("AME_DEBUG") else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("ame")

# Métricas Prometheus
REQUEST_COUNT = Counter("ame_requests_total", "Total requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("ame_request_latency_seconds", "Latency", ["endpoint"])
ACTIVE_AGENTS = Gauge("ame_active_agents", "Active agents")
REVENUE_GAUGE = Gauge("ame_revenue_total", "Total revenue")
PROFIT_GAUGE = Gauge("ame_profit_total", "Profit")
EXPERIMENTS_GAUGE = Gauge("ame_experiments_active", "Active experiments")
AI_COST_GAUGE = Gauge("ame_ai_cost_usd", "AI cost")
ERROR_COUNT = Counter("ame_errors_total", "Errors", ["type"])

def log_event(event: str, **kwargs):
    logger.info(event, **kwargs)

def log_error(error: str, **kwargs):
    logger.error(error, **kwargs)
    ERROR_COUNT.labels(type=kwargs.get("type", "unknown")).inc()

class MetricsStore:
    """Store simples para dashboard quando prometheus não está disponível"""
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.latencies: Dict[str, list] = {}
        self.events: list = []
    
    def inc(self, name: str, value: int = 1):
        self.counters[name] = self.counters.get(name, 0) + value

    def record_latency(self, endpoint: str, latency: float):
        self.latencies.setdefault(endpoint, []).append(latency)
        # mantém últimas 100
        if len(self.latencies[endpoint]) > 100:
            self.latencies[endpoint] = self.latencies[endpoint][-100:]

    def add_event(self, event: str, data: Dict[str, Any]):
        self.events.append({"event": event, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()})
        if len(self.events) > 500:
            self.events = self.events[-500:]

metrics_store = MetricsStore()

def get_health_status(db_ok: bool = True, ai_ok: bool = True) -> Dict[str, Any]:
    return {
        "status": "healthy" if db_ok else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "up" if db_ok else "down",
            "ai_router": "up" if ai_ok else "down",
            "orchestrator": "up",
            "event_bus": "up",
        },
        "uptime_seconds": time.time() - _start_time,
    }

_start_time = time.time()
