from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from app.core.security import rate_limit
from app.core.database import SyncSessionLocal
from app.models.base import Product, Offer
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str = "digital"
    price: float = 0.0
    cost: float = 0.0
    status: str = "draft"
    content: dict = {}
    assets: dict = {}

@router.get("")
def list_products(status: Optional[str] = None):
    db = SyncSessionLocal()
    try:
        q = db.query(Product)
        if status:
            q = q.filter(Product.status == status)
        products = q.order_by(Product.created_at.desc()).limit(50).all()
        return {"products": [{"id": p.id, "name": p.name, "type": p.type, "price": p.price, "status": p.status, "sales_count": p.sales_count, "revenue_total": p.revenue_total, "created_at": p.created_at.isoformat() if p.created_at else None} for p in products], "total": q.count()}
    finally:
        db.close()

@router.post("")
def create_product(req: ProductCreate, request: Request):
    rate_limit(request, limit=20)
    db = SyncSessionLocal()
    try:
        p = Product(id=str(uuid.uuid4())[:12], name=req.name, description=req.description, type=req.type, price=req.price, cost=req.cost, status=req.status, content=req.content, assets=req.assets, created_at=datetime.now(timezone.utc))
        db.add(p)
        db.commit()
        db.refresh(p)
        return {"id": p.id, "name": p.name, "status": p.status}
    finally:
        db.close()

@router.get("/{product_id}")
def get_product(product_id: str):
    db = SyncSessionLocal()
    try:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"id": p.id, "name": p.name, "description": p.description, "type": p.type, "price": p.price, "status": p.status, "content": p.content, "assets": p.assets}
    finally:
        db.close()

# Discovery, validation, creation pipeline endpoints
@router.post("/discover")
async def discover_products(niche_hint: str = "renda extra"):
    from app.services.discovery import discovery_service
    result = await discovery_service.discover(niche_hint=niche_hint)
    return result

@router.post("/validate")
async def validate_product(opportunity: dict):
    from app.services.validation import validation_service
    result = await validation_service.validate(opportunity)
    return result

@router.post("/create-bundle")
async def create_bundle(validated: dict):
    from app.services.creation import creation_service
    result = await creation_service.create_product(validated)
    # Also save to DB
    db = SyncSessionLocal()
    try:
        p = Product(id=str(uuid.uuid4())[:12], name=result.get("product","Produto AME"), description=str(result.get("strategy",{}).get("nome","")), type="digital", price=result.get("strategy",{}).get("preco",97), status="live", content=result, created_at=datetime.now(timezone.utc))
        db.add(p)
        db.commit()
    except Exception as e:
        print(f"DB save failed: {e}")
    finally:
        db.close()
    return result
