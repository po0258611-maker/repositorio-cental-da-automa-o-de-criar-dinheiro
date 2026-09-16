"""
AME - Tool System
Abstração para ferramentas com name, description, input, output, cost, risk, permissions, timeout, retry
Permite adicionar ferramentas sem modificar núcleo
"""
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time
import asyncio
from app.core.observability import logger

class ToolRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0  # custo estimado em USD
    risk: ToolRisk = ToolRisk.LOW
    permissions: List[str] = field(default_factory=list)
    timeout: int = 30
    retry: int = 1
    is_async: bool = False

    async def execute(self, **kwargs) -> Dict[str, Any]:
        start = time.time()
        last_error = None
        for attempt in range(self.retry + 1):
            try:
                logger.info("tool_execute", tool=self.name, attempt=attempt, kwargs=kwargs)
                if self.is_async:
                    result = await asyncio.wait_for(self.func(**kwargs), timeout=self.timeout)
                else:
                    # roda sync em thread para não bloquear
                    result = await asyncio.wait_for(asyncio.to_thread(self.func, **kwargs), timeout=self.timeout)
                elapsed = time.time() - start
                logger.info("tool_success", tool=self.name, elapsed=elapsed)
                return {"success": True, "data": result, "cost": self.cost, "elapsed": elapsed}
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout}s"
                logger.error("tool_timeout", tool=self.name, timeout=self.timeout)
            except Exception as e:
                last_error = str(e)
                logger.error("tool_failed", tool=self.name, error=str(e))
                if attempt < self.retry:
                    await asyncio.sleep(1 * (attempt + 1))
        return {"success": False, "error": last_error, "cost": 0.0}

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        logger.info("tool_registered", tool=tool.name, cost=tool.cost, risk=tool.risk)

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list(self) -> List[Tool]:
        return list(self._tools.values())

    def list_by_risk(self, max_risk: ToolRisk) -> List[Tool]:
        order = {ToolRisk.LOW: 0, ToolRisk.MEDIUM: 1, ToolRisk.HIGH: 2, ToolRisk.CRITICAL: 3}
        max_val = order[max_risk]
        return [t for t in self._tools.values() if order[t.risk] <= max_val]

    async def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        tool = self.get(name)
        if not tool:
            return {"success": False, "error": f"Tool {name} not found"}
        return await tool.execute(**kwargs)

# Global registry
tool_registry = ToolRegistry()

def tool(name: str, description: str = "", cost: float = 0.0, risk: ToolRisk = ToolRisk.LOW, timeout: int = 30, retry: int = 1, permissions: Optional[List[str]] = None):
    """Decorator para registrar função como Tool"""
    def decorator(func: Callable):
        is_async = asyncio.iscoroutinefunction(func)
        t = Tool(
            name=name,
            description=description or func.__doc__ or "",
            func=func,
            cost=cost,
            risk=risk,
            timeout=timeout,
            retry=retry,
            permissions=permissions or [],
            is_async=is_async
        )
        tool_registry.register(t)
        return func
    return decorator

# Exemplo de tools base que serão expandidas pelos agentes
@tool(name="web_search", description="Busca na web por tendências/oportunidades", cost=0.01, risk=ToolRisk.LOW)
def web_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    # Simulado - em produção usaria SerpAPI/Tavily
    return [{"title": f"Resultado para {query} #{i}", "url": f"https://example.com/{query}/{i}", "snippet": f"Snippet sobre {query}"} for i in range(limit)]

@tool(name="generate_text", description="Gera texto com LLM Router", cost=0.02, risk=ToolRisk.LOW)
def generate_text(prompt: str, max_tokens: int = 500) -> str:
    # Delegará para llm_router
    from app.core.llm_router import llm_router
    return llm_router.generate(prompt, max_tokens=max_tokens, task_type="simple")

@tool(name="create_file", description="Cria arquivo no workspace", cost=0.0, risk=ToolRisk.MEDIUM)
def create_file(path: str, content: str) -> Dict[str, Any]:
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"path": str(p), "size": len(content)}

@tool(name="send_telegram", description="Envia mensagem Telegram", cost=0.0, risk=ToolRisk.LOW)
def send_telegram(message: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
    # Simulado - em prod usa python-telegram-bot
    return {"sent": True, "message": message[:100], "chat_id": chat_id or "default"}

@tool(name="record_sale", description="Registra venda no Economic Engine", cost=0.0, risk=ToolRisk.LOW)
def record_sale(amount: float, product: str, channel: str = "direct") -> Dict[str, Any]:
    from app.core.economic import economic_engine
    return economic_engine.record_revenue(amount, description=f"Sale: {product}", channel=channel)

@tool(name="analyze_metrics", description="Analisa métricas de conversão", cost=0.0, risk=ToolRisk.LOW)
def analyze_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    # Simula análise
    ctr = metrics.get("ctr", 0)
    conv = metrics.get("conversion", 0)
    rec = "Manter" if conv > 0.02 else "Otimizar criativo"
    return {"recommendation": rec, "ctr": ctr, "conversion": conv}
