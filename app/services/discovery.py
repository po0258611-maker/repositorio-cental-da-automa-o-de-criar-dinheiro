"""
DISCOVERY SERVICE: pesquisa mercado, tendências, nichos, problemas, concorrentes, oportunidades, produtos, serviços, demandas
Orquestra Market, Trend, Competitor agents
"""
from typing import Dict, Any, List
from app.core.observability import logger
from app.core.events import emit, EventType

class DiscoveryService:
    async def discover(self, niche_hint: str = "renda extra") -> Dict[str, Any]:
        logger.info("discovery_start", hint=niche_hint)
        from app.agents import AGENTS
        market = await AGENTS["market_agent"].run(context={"hint": niche_hint})
        trend = await AGENTS["trend_agent"].run(context={"hint": niche_hint})
        competitor = await AGENTS["competitor_agent"].run(context={"hint": niche_hint})
        
        opportunities = market.get("opportunities", [])
        trends = trend.get("trends", [])
        competitors = competitor.get("competitors", [])
        
        # Scoring simples
        for opp in opportunities:
            opp["discovery_score"] = opp.get("score", 70) + (10 if any(t["trend"] in str(opp) for t in trends) else 0)
        
        result = {
            "niche_hint": niche_hint,
            "opportunities": opportunities,
            "trends": trends,
            "competitors": competitors,
            "top_opportunity": max(opportunities, key=lambda x: x.get("discovery_score",0)) if opportunities else None
        }
        emit(EventType.OpportunityFound, result, source="discovery_service")
        logger.info("discovery_done", top=result["top_opportunity"])
        return result

discovery_service = DiscoveryService()
