#!/usr/bin/env python3
"""Init DB - cria tabelas e dados iniciais"""
import sys
sys.path.insert(0, ".")

from app.core.database import init_db, SyncSessionLocal
from app.models.base import Agent, Integration, SystemSettings, Product, Experiment
from datetime import datetime, timezone

def seed_agents():
    db = SyncSessionLocal()
    try:
        from app.agents import AGENTS
        for name, agent in AGENTS.items():
            existing = db.query(Agent).filter(Agent.name == name).first()
            if not existing:
                db.add(Agent(
                    name=name,
                    display_name=agent.display_name,
                    description=agent.description,
                    category=agent.category,
                    is_active=True,
                    created_at=datetime.now(timezone.utc)
                ))
        db.commit()
        print(f"✅ {len(AGENTS)} agents seeded")
    finally:
        db.close()

def seed_integrations():
    db = SyncSessionLocal()
    try:
        defaults = [
            ("openai", "llm"), ("gemini", "llm"), ("telegram", "messaging"),
            ("stripe", "payment"), ("brevo", "email"), ("n8n", "automation")
        ]
        for name, type_ in defaults:
            if not db.query(Integration).filter(Integration.name == name).first():
                db.add(Integration(name=name, type=type_, is_active=False, config={}, created_at=datetime.now(timezone.utc)))
        db.commit()
        print("✅ Integrations seeded")
    finally:
        db.close()

def seed_settings():
    db = SyncSessionLocal()
    try:
        settings = [
            ("ame_version", "1.0.0", "AME version"),
            ("loop_interval", 60, "Orchestrator loop interval seconds"),
            ("max_daily_ai_cost", 10.0, "Max AI cost per day USD"),
        ]
        for key, val, desc in settings:
            if not db.query(SystemSettings).filter(SystemSettings.key == key).first():
                db.add(SystemSettings(key=key, value=val, description=desc))
        db.commit()
        print("✅ Settings seeded")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Initializing AME Database...")
    init_db()
    seed_agents()
    seed_integrations()
    seed_settings()
    print("✅ Database ready!")
