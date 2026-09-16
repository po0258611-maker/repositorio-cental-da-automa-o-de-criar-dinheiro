"""
AME - BaseAgent
Todos os agentes herdam desta classe
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from app.core.observability import logger
from app.core.memory import memory_store
from app.core.tools import tool_registry

class BaseAgent:
    def __init__(self, name: str, display_name: str, category: str, description: str = ""):
        self.name = name
        self.display_name = display_name
        self.category = category
        self.description = description
        self.id = str(uuid.uuid4())[:8]
        self.total_runs = 0
        self.last_run: Optional[datetime] = None
        self.last_result: Optional[Dict[str, Any]] = None

    async def run(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Override in subclasses"""
        self.total_runs += 1
        self.last_run = datetime.now(timezone.utc)
        logger.info("agent_run", agent=self.name, context=context)
        result = await self.execute(context or {})
        self.last_result = result
        return result

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def remember(self, action: str, result: str, lesson: str = "", **kwargs):
        category_map = {
            "RESEARCH": "market_memory",
            "PRODUCT": "product_memory",
            "CREATIVE": "marketing_memory",
            "GROWTH": "marketing_memory",
            "FINANCE": "financial_memory",
            "QUALITY": "system_memory",
            "LEARNING": "experiment_memory",
            "CORE": "system_memory",
        }
        cat = category_map.get(self.category, "system_memory")
        return memory_store.add(category=cat, action=f"{self.name}:{action}", result=result, lesson=lesson, **kwargs)

    def get_tools(self):
        return tool_registry.list()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "category": self.category,
            "description": self.description,
            "total_runs": self.total_runs,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_result": self.last_result,
        }
