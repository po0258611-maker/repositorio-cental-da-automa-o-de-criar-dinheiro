
"""
AME - Tool System
Controlled tool abstraction with timeout/retry/risk metadata.

Tools that are not configured for real execution return an explicit
NOT_CONFIGURED result instead of fabricating a successful operation.
"""
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time
import asyncio
import httpx

from app.core.observability import logger
from app.core.config import settings


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
    cost: float = 0.0
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
                safe_kwargs = {k: v for k, v in kwargs.items() if k not in {"api_key", "token", "secret"}}
                logger.info("tool_execute", tool=self.name, attempt=attempt, kwargs=safe_kwargs)
                if self.is_async:
                    result = await asyncio.wait_for(self.func(**kwargs), timeout=self.timeout)
                else:
                    result = await asyncio.wait_for(asyncio.to_thread(self.func, **kwargs), timeout=self.timeout)
                elapsed = time.time() - start
                logger.info("tool_success", tool=self.name, elapsed=elapsed)
                return {"success": True, "data": result, "cost": self.cost, "elapsed": elapsed}
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout}s"
                logger.error("tool_timeout", tool=self.name, timeout=self.timeout)
            except Exception as exc:
                last_error = str(exc)
                logger.error("tool_failed", tool=self.name, error=str(exc))
                if attempt < self.retry:
                    await asyncio.sleep(1 * (attempt + 1))
        return {"success": False, "error": last_error, "cost": 0.0}


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        logger.info("tool_registered", tool=tool.name, cost=tool.cost, risk=tool.risk.value)

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
            return {"success": False, "status": "NOT_FOUND", "error": f"Tool {name} not found"}
        return await tool.execute(**kwargs)


tool_registry = ToolRegistry()


def tool(
    name: str,
    description: str = "",
    cost: float = 0.0,
    risk: ToolRisk = ToolRisk.LOW,
    timeout: int = 30,
    retry: int = 1,
    permissions: Optional[List[str]] = None,
):
    def decorator(func: Callable):
        t = Tool(
            name=name,
            description=description or func.__doc__ or "",
            func=func,
            cost=cost,
            risk=risk,
            timeout=timeout,
            retry=retry,
            permissions=permissions or [],
            is_async=asyncio.iscoroutinefunction(func),
        )
        tool_registry.register(t)
        return func

    return decorator


@tool(
    name="web_search",
    description="Busca resultados reais na web usando Tavily ou Serper.",
    cost=0.01,
    risk=ToolRisk.LOW,
)
async def web_search(query: str, limit: int = 5) -> Dict[str, Any]:
    from app.core.research import research_engine
    return await research_engine.search(query=query, limit=limit)


@tool(
    name="fetch_url",
    description="Baixa uma página HTTP/HTTPS e registra evidência.",
    cost=0.0,
    risk=ToolRisk.MEDIUM,
)
async def fetch_url(url: str) -> Dict[str, Any]:
    from app.core.research import research_engine
    return await research_engine.fetch_url(url)


@tool(name="generate_text", description="Gera texto com LLM Router", cost=0.02, risk=ToolRisk.LOW)
def generate_text(prompt: str, max_tokens: int = 500) -> str:
    from app.core.llm_router import llm_router
    return llm_router.generate(prompt, max_tokens=max_tokens, task_type="simple")


@tool(
    name="create_file",
    description="Cria arquivo somente dentro do workspace do AME.",
    cost=0.0,
    risk=ToolRisk.MEDIUM,
    permissions=["write"],
)
def create_file(path: str, content: str) -> Dict[str, Any]:
    requested = Path(path)
    if requested.is_absolute() or ".." in requested.parts:
        return {"status": "DENIED", "reason": "Path must stay inside the AME workspace"}
    root = Path.cwd().resolve()
    target = (root / requested).resolve()
    if root not in target.parents and target != root:
        return {"status": "DENIED", "reason": "Path escapes workspace"}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"status": "OK", "path": str(target.relative_to(root)), "size": len(content)}


@tool(
    name="send_telegram",
    description="Envia mensagem real via Telegram Bot API quando configurado.",
    cost=0.0,
    risk=ToolRisk.HIGH,
    permissions=["message"],
)
async def send_telegram(message: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
    token = settings.telegram_bot_token
    target = chat_id or settings.telegram_chat_id
    if not token or not target:
        return {
            "status": "NOT_CONFIGURED",
            "sent": False,
            "message": "Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.",
        }
    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(endpoint, json={"chat_id": target, "text": message[:4096]})
            response.raise_for_status()
            data = response.json()
        return {"status": "OK", "sent": bool(data.get("ok")), "provider": "telegram"}
    except Exception as exc:
        logger.error("telegram_send_failed", error=str(exc))
        return {"status": "ERROR", "sent": False, "error": str(exc)}


@tool(name="record_sale", description="Registra venda no Economic Engine", cost=0.0, risk=ToolRisk.HIGH, permissions=["financial"])
def record_sale(amount: float, product: str, channel: str = "direct") -> Dict[str, Any]:
    from app.core.economic import economic_engine
    return economic_engine.record_revenue(amount, description=f"Sale: {product}", channel=channel)


@tool(name="analyze_metrics", description="Analisa métricas observadas", cost=0.0, risk=ToolRisk.LOW)
def analyze_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    ctr = metrics.get("ctr")
    conv = metrics.get("conversion")
    if conv is None:
        return {"status": "INSUFFICIENT_DATA", "ctr": ctr, "conversion": None}
    rec = "Manter" if conv > 0.02 else "Otimizar criativo"
    return {"status": "OK", "recommendation": rec, "ctr": ctr, "conversion": conv}
