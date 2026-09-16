"""
DISTRIBUTION SERVICE: automatiza conteúdo, SEO, email, anúncios, páginas, campanhas, coleta métricas
"""
from typing import Dict, Any
from app.core.observability import logger
from app.core.events import emit, EventType

class DistributionService:
    async def distribute(self, product_bundle: Dict[str, Any], channels: list = ["social","seo","email"]) -> Dict[str, Any]:
        logger.info("distribution_start", product=product_bundle.get("product"), channels=channels)
        from app.agents import AGENTS
        results = {}
        if "social" in channels:
            results["social"] = await AGENTS["social_agent"].run(context={"product": product_bundle})
        if "seo" in channels:
            results["seo"] = await AGENTS["seo_agent"].run(context={"product": product_bundle, "keyword": product_bundle.get("strategy",{}).get("nome","automação")})
        if "email" in channels:
            results["email"] = await AGENTS["email_agent"].run(context={"product": product_bundle})
        if "ads" in channels:
            results["ads"] = await AGENTS["ads_agent"].run(context={"product": product_bundle, "budget": 20})
        
        emit(EventType.CampaignCreated, {"channels": channels, "results": results}, source="distribution_service")
        logger.info("distribution_done", channels=channels)
        return {"channels": channels, "results": results, "product": product_bundle.get("product")}

distribution_service = DistributionService()
