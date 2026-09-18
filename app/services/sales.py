"""
SALES SERVICE: funnel analysis based on persisted leads and sales.

This service does not fabricate leads or conversions. It reports observed data
and delegates copy/offer work to the sales agent.
"""
from typing import Dict, Any, Optional
from sqlalchemy import func

from app.core.observability import logger
from app.core.database import SyncSessionLocal
from app.models.base import Lead, Sale, Product
from app.core.events import emit, EventType


class SalesService:
    async def sell(self, product_bundle: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("sales_start", product=product_bundle.get("product"))
        from app.agents import AGENTS

        sales = await AGENTS["sales_agent"].run(context={"product": product_bundle})

        product_id: Optional[str] = product_bundle.get("product_id")
        db = SyncSessionLocal()
        try:
            lead_query = db.query(Lead)
            sale_query = db.query(Sale)
            if product_id:
                sale_query = sale_query.filter(Sale.product_id == product_id)

            total_leads = lead_query.count()
            qualified_leads = lead_query.filter(Lead.status.in_(["qualified", "converted"])).count()
            converted_leads = lead_query.filter(Lead.status == "converted").count()
            sales_count = sale_query.filter(Sale.status == "completed").count()
            revenue = sale_query.filter(Sale.status == "completed").with_entities(
                func.coalesce(func.sum(Sale.amount), 0)
            ).scalar() or 0

            leads = {
                "observed": True,
                "new_leads": lead_query.filter(Lead.status == "new").count(),
                "qualified": qualified_leads,
                "converted": converted_leads,
                "sales": sales_count,
                "revenue": float(revenue),
                "total_leads": total_leads,
            }

            if total_leads == 0 and sales_count == 0:
                status = "NO_OBSERVED_TRAFFIC"
            else:
                status = "OK"

            result = {
                "status": status,
                "sales": sales,
                "leads": leads,
                "funnel": sales.get("funnel"),
            }
            emit(EventType.SaleCreated, result, source="sales_service")
            logger.info("sales_done", status=status, leads=total_leads, sales=sales_count)
            return result
        finally:
            db.close()


sales_service = SalesService()
