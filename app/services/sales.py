"""
SALES SERVICE: ofertas, landing, checkout, leads, acompanhamento, métricas, conversão, funil
"""
from typing import Dict, Any
from app.core.observability import logger
from app.core.events import emit, EventType

class SalesService:
    async def sell(self, product_bundle: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("sales_start", product=product_bundle.get("product"))
        from app.agents import AGENTS
        sales = await AGENTS["sales_agent"].run(context={"product": product_bundle})
        # Simula captura de leads
        leads = {"new_leads": 45, "qualified": 12, "converted": 3}
        emit(EventType.LeadGenerated, leads, source="sales_service")
        emit(EventType.SaleCreated, {"leads": leads, "sales": sales.get("funnel")}, source="sales_service")
        logger.info("sales_done", leads=leads)
        return {"sales": sales, "leads": leads, "funnel": sales.get("funnel")}

sales_service = SalesService()
