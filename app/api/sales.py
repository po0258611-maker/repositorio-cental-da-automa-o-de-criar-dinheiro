from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from app.core.security import rate_limit
from app.core.database import SyncSessionLocal
from app.models.base import Sale, Lead, Customer
from datetime import datetime, timezone
import uuid

router = APIRouter()

class LeadCreate(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = "direct"
    campaign_id: Optional[str] = None

class SaleCreate(BaseModel):
    amount: float
    product_id: Optional[str] = None
    customer_email: Optional[str] = None
    channel: str = "direct"

@router.get("/leads")
def list_leads(limit: int = 20):
    db = SyncSessionLocal()
    try:
        leads = db.query(Lead).order_by(Lead.created_at.desc()).limit(limit).all()
        return {"leads": [{"id": l.id, "email": l.email, "name": l.name, "source": l.source, "status": l.status, "created_at": l.created_at.isoformat() if l.created_at else None} for l in leads], "total": db.query(Lead).count()}
    finally:
        db.close()

@router.post("/leads")
def create_lead(req: LeadCreate, request: Request):
    rate_limit(request, limit=50)
    db = SyncSessionLocal()
    try:
        lead = Lead(id=str(uuid.uuid4())[:12], email=req.email, name=req.name, phone=req.phone, source=req.source, campaign_id=req.campaign_id, created_at=datetime.now(timezone.utc))
        db.add(lead)
        db.commit()
        # evento
        try:
            from app.core.events import emit, EventType
            emit(EventType.LeadGenerated, {"lead_id": lead.id, "email": lead.email, "source": lead.source}, source="sales_api")
        except:
            pass
        return {"id": lead.id, "email": lead.email, "status": lead.status}
    finally:
        db.close()

@router.get("/sales")
def list_sales(limit: int = 20):
    db = SyncSessionLocal()
    try:
        sales = db.query(Sale).order_by(Sale.created_at.desc()).limit(limit).all()
        total_revenue = sum(s.amount for s in sales)
        return {"sales": [{"id": s.id, "amount": s.amount, "status": s.status, "created_at": s.created_at.isoformat() if s.created_at else None} for s in sales], "total": db.query(Sale).count(), "revenue": total_revenue}
    finally:
        db.close()

@router.post("/sales")
def create_sale(req: SaleCreate, request: Request):
    rate_limit(request, limit=50)
    db = SyncSessionLocal()
    try:
        sale = Sale(id=str(uuid.uuid4())[:12], amount=req.amount, product_id=req.product_id, status="completed", created_at=datetime.now(timezone.utc))
        db.add(sale)
        # customer upsert
        if req.customer_email:
            cust = db.query(Customer).filter(Customer.email == req.customer_email).first()
            if not cust:
                cust = Customer(id=str(uuid.uuid4())[:12], email=req.customer_email, total_orders=1, total_spent=req.amount, first_purchase_at=datetime.now(timezone.utc), last_purchase_at=datetime.now(timezone.utc))
                db.add(cust)
            else:
                cust.total_orders += 1
                cust.total_spent += req.amount
                cust.last_purchase_at = datetime.now(timezone.utc)
            sale.customer_id = cust.id
        db.commit()
        # economic
        from app.core.economic import economic_engine
        economic_engine.record_revenue(req.amount, description=f"Sale {req.product_id}", channel=req.channel)
        try:
            from app.core.events import emit, EventType
            emit(EventType.SaleCreated, {"sale_id": sale.id, "amount": sale.amount, "channel": req.channel}, source="sales_api")
            emit(EventType.RevenueReceived, {"amount": req.amount, "channel": req.channel}, source="sales_api")
        except:
            pass
        return {"id": sale.id, "amount": sale.amount, "status": sale.status}
    finally:
        db.close()

@router.post("/funnel/run")
async def run_funnel(product_bundle: dict):
    from app.services.sales import sales_service
    result = await sales_service.sell(product_bundle)
    return result
