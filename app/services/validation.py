"""
VALIDATION SERVICE: demanda, concorrência, preço, monetização, experimentos, MVP, teste oferta/canal
"""
from typing import Dict, Any
from app.core.observability import logger
from app.core.events import emit, EventType

class ValidationService:
    async def validate(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("validation_start", opportunity=opportunity)
        from app.agents import AGENTS
        result = await AGENTS["validation_agent"].run(context={"opportunity": opportunity})
        validation = result.get("validation", {})
        
        # Economic validation
        econ = await AGENTS["economic_agent"].run(context={"opportunity": opportunity})
        pricing = await AGENTS["pricing_agent"].run(context={"opportunity": opportunity})
        
        combined = {
            "opportunity": opportunity,
            "validation": validation,
            "economic": econ.get("metrics"),
            "pricing": pricing.get("pricing"),
            "go": validation.get("recomendacao") == "GO",
            "mvp": validation.get("mvp_sugerido"),
        }
        if combined["go"]:
            emit(EventType.OpportunityValidated, combined, source="validation_service")
        logger.info("validation_done", go=combined["go"])
        return combined

validation_service = ValidationService()
