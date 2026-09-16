#!/usr/bin/env python3
"""Seed demo data: products, experiments, leads, sales"""
import sys
sys.path.insert(0, ".")
from app.core.database import SyncSessionLocal, init_db
from app.models.base import Product, Experiment, Lead, Sale, Customer
from datetime import datetime, timezone, timedelta
import uuid
from app.core.economic import economic_engine
from app.core.experiment import experiment_engine

def seed_demo():
    init_db()
    db = SyncSessionLocal()
    try:
        # Products
        if db.query(Product).count() == 0:
            p1 = Product(id=str(uuid.uuid4())[:12], name="IA Prática para Lojas Locais", description="Ebook + templates n8n", type="ebook", price=97, status="live", content={"chapters": 5}, created_at=datetime.now(timezone.utc))
            p2 = Product(id=str(uuid.uuid4())[:12], name="Pack PLR Lucrativo", description="100 PLRs com licença", type="plr", price=67, status="live", content={}, created_at=datetime.now(timezone.utc))
            db.add_all([p1,p2])
            db.commit()
            print("✅ Products seeded")

        # Leads
        if db.query(Lead).count() == 0:
            for i in range(5):
                l = Lead(id=str(uuid.uuid4())[:12], email=f"lead{i}@teste.com", name=f"Lead {i}", source="instagram", status="new", created_at=datetime.now(timezone.utc))
                db.add(l)
            db.commit()
            print("✅ Leads seeded")

        # Economic demo
        economic_engine.record_revenue(497, description="Demo sales", channel="hotmart")
        economic_engine.record_expense(23.50, description="OpenAI cost", category="ai_cost")

        # Experiments
        if len(experiment_engine.experiments) == 0:
            e1 = experiment_engine.create(name="Tripwire R$27", hypothesis="Tripwire aumenta conversão 40%", product="Ebook IA", channel="Instagram", budget=50, kpi="vendas")
            e1.add_cost(30)
            e1.add_revenue(194)
            e1.transition(e1.status.__class__.LIVE, "Seeding LIVE")
            e2 = experiment_engine.create(name="Ads Facebook R$20/dia", hypothesis="Ads com ROI >3", product="Pack PLR", channel="Facebook Ads", budget=100, kpi="roas")
            e2.add_cost(40)
            e2.add_revenue(0)
            e2.transition(e2.status.__class__.VALIDATING, "Seeding validating")
            print("✅ Experiments seeded")

        print("✅ Demo data ready")
        print(f"   Economic: {economic_engine.get_dashboard()}")
        print(f"   Experiments: {experiment_engine.stats()}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo()
