"""
AME - Event Architecture
Event Bus em memória + persistência opcional no DB
Eventos: OpportunityFound, ExperimentCreated, SaleCreated, etc.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Callable, Optional
from enum import Enum
import uuid
import asyncio
from app.core.observability import logger, metrics_store

class EventType(str, Enum):
    OpportunityFound = "OpportunityFound"
    OpportunityValidated = "OpportunityValidated"
    ExperimentCreated = "ExperimentCreated"
    ProductCreated = "ProductCreated"
    ProductPublished = "ProductPublished"
    CampaignCreated = "CampaignCreated"
    LeadGenerated = "LeadGenerated"
    SaleCreated = "SaleCreated"
    RevenueReceived = "RevenueReceived"
    ExpenseRecorded = "ExpenseRecorded"
    ExperimentWon = "ExperimentWon"
    ExperimentFailed = "ExperimentFailed"
    BudgetExceeded = "BudgetExceeded"
    RiskDetected = "RiskDetected"
    ApprovalRequired = "ApprovalRequired"
    AgentTaskCompleted = "AgentTaskCompleted"
    AgentTaskFailed = "AgentTaskFailed"
    SystemHealthCheck = "SystemHealthCheck"

class Event:
    def __init__(self, type: EventType, payload: Dict[str, Any], source: str = "system", correlation_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.type = type
        self.payload = payload
        self.source = source
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
        self.acked = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
        }

class EventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._history: List[Event] = []
        self._max_history = 1000

    def subscribe(self, event_type: EventType, handler: Callable):
        self._handlers.setdefault(event_type, []).append(handler)
        logger.info("event_subscribed", event_type=event_type, handler=handler.__name__)

    def unsubscribe(self, event_type: EventType, handler: Callable):
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]

    async def publish(self, event: Event):
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        metrics_store.add_event(event.type, event.payload)
        logger.info("event_published", event_type=event.type, source=event.source, payload=event.payload)
        
        handlers = self._handlers.get(event.type, []) + self._handlers.get("*", [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error("event_handler_failed", event_type=event.type, handler=handler.__name__, error=str(e))

    def publish_sync(self, event: Event):
        """Versão síncrona para uso fora de async"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.publish(event))
            else:
                loop.run_until_complete(self.publish(event))
        except RuntimeError:
            # sem loop, executa handlers sync
            self._history.append(event)
            for handler in self._handlers.get(event.type, []):
                try:
                    if not asyncio.iscoroutinefunction(handler):
                        handler(event)
                except Exception as e:
                    logger.error("event_handler_sync_failed", error=str(e))

    def history(self, limit: int = 50, event_type: Optional[EventType] = None) -> List[Dict[str, Any]]:
        filtered = self._history
        if event_type:
            filtered = [e for e in filtered if e.type == event_type]
        return [e.to_dict() for e in filtered[-limit:]]

    def clear(self):
        self._history.clear()
        self._handlers.clear()

# Singleton global
event_bus = EventBus()

# Helper para publicar rapidamente
def emit(event_type: EventType, payload: Dict[str, Any], source: str = "system"):
    event = Event(type=event_type, payload=payload, source=source)
    event_bus.publish_sync(event)
    return event
