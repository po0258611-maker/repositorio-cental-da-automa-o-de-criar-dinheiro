from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, List
from app.core.security import rate_limit

router = APIRouter()

class CampaignCreate(BaseModel):
    name: str
    channel: str = "social"
    budget: float = 0.0
    product_id: Optional[str] = None

# In-memory campaigns for MVP (persist in DB in prod)
_campaigns = []

@router.get("/campaigns")
def list_campaigns(channel: Optional[str] = None):
    filtered = [c for c in _campaigns if not channel or c["channel"]==channel]
    return {"campaigns": filtered, "total": len(filtered)}

@router.post("/campaigns")
def create_campaign(req: CampaignCreate, request: Request):
    rate_limit(request, limit=20)
    camp = {"id": str(len(_campaigns)+1), "name": req.name, "channel": req.channel, "budget": req.budget, "product_id": req.product_id, "status": "draft", "impressions": 0, "clicks": 0, "leads": 0, "sales": 0}
    _campaigns.append(camp)
    return camp

@router.post("/distribute")
async def distribute(product_bundle: dict, channels: List[str] = ["social","seo","email"]):
    from app.services.distribution import distribution_service
    result = await distribution_service.distribute(product_bundle, channels=channels)
    return result

@router.post("/seo/generate")
async def seo_generate(keyword: str = "automação com IA"):
    from app.agents import AGENTS
    result = await AGENTS["seo_agent"].run(context={"keyword": keyword})
    return result

@router.post("/social/schedule")
async def social_schedule():
    from app.agents import AGENTS
    result = await AGENTS["social_agent"].run(context={})
    return result

@router.post("/ads/create")
async def ads_create(budget: float = 20):
    from app.agents import AGENTS
    result = await AGENTS["ads_agent"].run(context={"budget": budget})
    return result

@router.post("/email/sequence")
async def email_sequence():
    from app.agents import AGENTS
    result = await AGENTS["email_agent"].run(context={})
    return result
