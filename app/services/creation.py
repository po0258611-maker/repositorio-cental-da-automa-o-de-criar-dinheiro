"""
CREATION SERVICE: produz automaticamente ebooks, PDFs, imagens, copies, posts, vídeos, landing pages, etc
Orquestra Product + Creative agents
"""
from typing import Dict, Any
from app.core.observability import logger
from app.core.events import emit, EventType

class CreationService:
    async def create_product(self, validated_opportunity: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("creation_start", opportunity=validated_opportunity.get("opportunity"))
        from app.agents import AGENTS
        
        # Estratégia
        strat = await AGENTS["product_strategist_agent"].run(context={"validation": validated_opportunity.get("validation", {})})
        strategy = strat.get("strategy", {})
        
        # Build
        built = await AGENTS["product_builder_agent"].run(context={"strategy": strategy})
        digital = await AGENTS["digital_product_agent"].run(context={"strategy": strategy})
        landing = await AGENTS["landing_page_agent"].run(context={"strategy": strategy})
        
        # Creative
        copy = await AGENTS["copy_agent"].run(context={"strategy": strategy})
        image = await AGENTS["image_agent"].run(context={"strategy": strategy})
        video = await AGENTS["video_agent"].run(context={"strategy": strategy})
        content = await AGENTS["content_agent"].run(context={"strategy": strategy, "tema": strategy.get("nome","renda extra")})
        
        result = {
            "strategy": strategy,
            "product": built.get("product"),
            "product_path": built.get("path"),
            "templates": digital.get("templates"),
            "landing": landing.get("landing_path"),
            "copies": copy.get("copies"),
            "image": image.get("path"),
            "video": video.get("roteiro"),
            "content": content.get("posts"),
        }
        emit(EventType.ProductPublished, result, source="creation_service")
        logger.info("creation_done", product=result["product"])
        return result

creation_service = CreationService()
