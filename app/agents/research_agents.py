"""
RESEARCH AGENTS: MARKET, TREND, COMPETITOR, VALIDATION

All market signals now originate from the real Research Engine. No fabricated
scores, static competitors, or random GO/NO-GO decisions are allowed.
"""
from __future__ import annotations

from typing import Dict, Any, List
from urllib.parse import urlparse

from app.agents.base import BaseAgent
from app.core.llm_router import llm_router
from app.core.tools import tool_registry
from app.core.events import emit, EventType


def _domains(results: List[Dict[str, Any]]) -> List[str]:
    domains = []
    for item in results:
        url = item.get("url") or item.get("source_url") or ""
        try:
            host = urlparse(url).netloc.lower()
        except Exception:
            host = ""
        if host and host not in domains:
            domains.append(host)
    return domains


class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="market_agent",
            display_name="MARKET_AGENT",
            category="RESEARCH",
            description="Pesquisa real de mercado, nichos, problemas e demanda.",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        hint = context.get("hint") or context.get("niche_hint") or "produtos digitais Brasil"
        tool = tool_registry.get("web_search")
        if not tool:
            return {"status": "NOT_READY", "reason": "web_search tool unavailable", "opportunities": []}

        query = f"{hint} demanda Brasil 2026 mercado consumidores problemas produtos digitais"
        search = await tool.execute(query=query, limit=8)
        data = search.get("data") if search.get("success") else search
        if not isinstance(data, dict) or data.get("status") != "OK":
            return {
                "status": data.get("status", "ERROR") if isinstance(data, dict) else "ERROR",
                "query": query,
                "opportunities": [],
                "evidence": data.get("evidence", []) if isinstance(data, dict) else [],
                "error": data.get("error") if isinstance(data, dict) else search.get("error"),
            }

        results = data.get("results", [])
        evidence = data.get("evidence", [])
        prompt = (
            "A partir SOMENTE das evidências abaixo, identifique até 5 oportunidades de "
            "produtos digitais. Não invente números. Retorne JSON com niche, problem, audience, "
            "signals e evidence_ids.\n\n"
            + str([{
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content") or r.get("snippet", ""),
            } for r in results])
        )
        opportunities: List[Dict[str, Any]] = []
        try:
            text = llm_router.generate(prompt, task_type="medium", max_tokens=900)
        except Exception as exc:
            return {
                "status": "RESEARCH_OK_LLM_UNAVAILABLE",
                "query": query,
                "results": results,
                "evidence": evidence,
                "opportunities": [],
                "llm_error": str(exc),
            }
        # Keep model output as analysis rather than treating unparsed text as structured fact.
        result = {
            "status": "OK",
            "query": query,
            "provider": data.get("provider"),
            "results": results,
            "evidence": evidence,
            "source_domains": _domains(results),
            "analysis": text,
            "opportunities": opportunities,
        }
        emit(EventType.OpportunityFound, {"agent": self.name, **result}, source=self.name)
        self.remember(
            "market_research",
            f"Real research collected: {len(results)} sources",
            lesson="Use only source-backed opportunities",
            metric={"sources": len(results), "domains": len(_domains(results))},
        )
        return result


class TrendAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="trend_agent",
            display_name="TREND_AGENT",
            category="RESEARCH",
            description="Monitora tendências com evidência web.",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        hint = context.get("hint") or "tendências IA automação pequenos negócios Brasil"
        tool = tool_registry.get("web_search")
        search = await tool.execute(query=hint, limit=8) if tool else {"success": False, "error": "web_search unavailable"}
        data = search.get("data") if search.get("success") else search
        if not isinstance(data, dict) or data.get("status") != "OK":
            return {
                "status": data.get("status", "ERROR") if isinstance(data, dict) else "ERROR",
                "trends": [],
                "evidence": data.get("evidence", []) if isinstance(data, dict) else [],
            }
        results = data.get("results", [])
        trends = [
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "signal": item.get("content") or item.get("snippet", ""),
            }
            for item in results
        ]
        self.remember("trend_analysis", f"Collected {len(trends)} real trend signals", metric={"trends": len(trends)})
        return {
            "status": "OK",
            "query": hint,
            "provider": data.get("provider"),
            "trends": trends,
            "evidence": data.get("evidence", []),
            "source_domains": _domains(results),
        }


class CompetitorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="competitor_agent",
            display_name="COMPETITOR_AGENT",
            category="RESEARCH",
            description="Pesquisa concorrentes, preços e ofertas na web.",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        niche = context.get("hint") or context.get("niche") or "produtos digitais IA para pequenos negócios"
        tool = tool_registry.get("web_search")
        query = f"{niche} concorrentes preço oferta Brasil"
        search = await tool.execute(query=query, limit=8) if tool else {"success": False, "error": "web_search unavailable"}
        data = search.get("data") if search.get("success") else search
        if not isinstance(data, dict) or data.get("status") != "OK":
            return {
                "status": data.get("status", "ERROR") if isinstance(data, dict) else "ERROR",
                "competitors": [],
                "evidence": data.get("evidence", []) if isinstance(data, dict) else [],
            }
        results = data.get("results", [])
        competitors = [
            {
                "name": item.get("title"),
                "url": item.get("url"),
                "signal": item.get("content") or item.get("snippet", ""),
            }
            for item in results
        ]
        analysis = ""
        try:
            analysis = llm_router.generate(
                f"Analise SOMENTE estes resultados de concorrentes e destaque padrões de preço/oferta, sem inventar dados: {competitors}",
                task_type="simple",
                max_tokens=600,
            )
        except Exception:
            analysis = ""
        return {
            "status": "OK",
            "query": query,
            "provider": data.get("provider"),
            "competitors": competitors,
            "analysis": analysis,
            "evidence": data.get("evidence", []),
            "source_domains": _domains(results),
        }


class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="validation_agent",
            display_name="VALIDATION_AGENT",
            category="RESEARCH",
            description="Valida uma oportunidade somente quando há evidência suficiente.",
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        opportunity = context.get("opportunity") or {}
        evidence = opportunity.get("evidence") or context.get("evidence") or []
        results = opportunity.get("results") or context.get("results") or []
        combined_count = len(evidence)
        domain_count = len(_domains(results)) if results else len({
            item.get("provider") for item in evidence if item.get("provider")
        })
        confidence = min(0.95, 0.20 + combined_count * 0.08 + max(0, domain_count - 1) * 0.10)

        # No evidence means no automatic GO.
        go = combined_count >= 3 and domain_count >= 2 and confidence >= 0.55
        recommendation = "GO" if go else "INSUFFICIENT_EVIDENCE"

        validation = {
            "status": "OK" if combined_count else "INSUFFICIENT_EVIDENCE",
            "evidence_count": combined_count,
            "source_diversity": domain_count,
            "confidence": round(confidence, 3),
            "recommendacao": recommendation,
            "preco_viavel": opportunity.get("price_hypothesis"),
            "monetizacao": opportunity.get("monetization_hypothesis"),
            "mvp_sugerido": opportunity.get("mvp_suggestion"),
            "canal_teste": opportunity.get("test_channel"),
        }

        if go:
            emit(EventType.OpportunityValidated, {"opportunity": opportunity, "validation": validation}, source=self.name)
            from app.core.experiment import experiment_engine
            exp = experiment_engine.create(
                name=f"Validar {opportunity.get('nicho', opportunity.get('name', 'oportunidade'))}",
                hypothesis=f"Existe demanda pagante para {opportunity}",
                product=validation.get("mvp_sugerido") or "MVP a definir",
                channel=validation.get("canal_teste") or "a definir",
                budget=0,
                kpi="vendas",
            )
            validation["experiment_id"] = exp.id

        self.remember(
            "validation",
            f"Validation={recommendation}; evidence={combined_count}",
            lesson="Automação só aprova oportunidade com evidência mínima.",
            metric=validation,
        )
        return {
            "status": validation["status"],
            "validation": validation,
            "lesson": f"Validação: {recommendation}",
        }
