from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.security import rate_limit
from app.core.database import SyncSessionLocal
from app.models.base import Campaign
from datetime import datetime, timezone
import uuid

router = APIRouter()


class CampaignCreate(BaseModel):
    name: str
    channel: str = "social"
    budget: float = 0.0
    product_id: Optional[str] = None


@router.get("/campaigns")
def list_campaigns(channel: Optional[str] = None, limit: int = 50):
    db = SyncSessionLocal()
    try:
        q = db.query(Campaign)
        if channel:
            q = q.filter(Campaign.channel == channel)
        rows = q.order_by(Campaign.created_at.desc()).limit(max(1, min(limit, 200))).all()
        return {
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "channel": c.channel,
                    "budget": c.budget,
                    "spend": c.spend,
                    "product_id": c.product_id,
                    "experiment_id": c.experiment_id,
                    "status": c.status,
                    "impressions": c.impressions,
                    "clicks": c.clicks,
                    "leads": c.leads,
                    "sales": c.sales,
                    "revenue": c.revenue,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in rows
            ],
            "total": q.count(),
        }
    finally:
        db.close()


@router.post("/campaigns")
def create_campaign(req: CampaignCreate, request: Request):
    rate_limit(request, limit=20)
    db = SyncSessionLocal()
    try:
        campaign = Campaign(
            id=str(uuid.uuid4())[:12],
            name=req.name,
            channel=req.channel,
            budget=req.budget,
            product_id=req.product_id,
            status="draft",
            created_at=datetime.now(timezone.utc),
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return {
            "id": campaign.id,
            "name": campaign.name,
            "channel": campaign.channel,
            "budget": campaign.budget,
            "status": campaign.status,
        }
    finally:
        db.close()


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str):
    db = SyncSessionLocal()
    try:
        c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {
            "id": c.id,
            "name": c.name,
            "channel": c.channel,
            "budget": c.budget,
            "spend": c.spend,
            "product_id": c.product_id,
            "experiment_id": c.experiment_id,
            "status": c.status,
            "impressions": c.impressions,
            "clicks": c.clicks,
            "leads": c.leads,
            "sales": c.sales,
            "revenue": c.revenue,
        }
    finally:
        db.close()


@router.post("/distribute")
async def distribute(product_bundle: dict, channels: List[str] = ["social", "seo", "email"]):
    from app.services.distribution import distribution_service
    return await distribution_service.distribute(product_bundle, channels=channels)


@router.post("/seo/generate")
async def seo_generate(keyword: str = "automação com IA"):
    from app.agents import AGENTS
    return await AGENTS["seo_agent"].run(context={"keyword": keyword})


@router.post("/social/schedule")
async def social_schedule():
    from app.agents import AGENTS
    return await AGENTS["social_agent"].run(context={})


@router.post("/ads/create")
async def ads_create(budget: float = 20):
    from app.agents import AGENTS
    return await AGENTS["ads_agent"].run(context={"budget": budget})


@router.post("/email/sequence")
async def email_sequence():
    from app.agents import AGENTS
    return await AGENTS["email_agent"].run(context={})
