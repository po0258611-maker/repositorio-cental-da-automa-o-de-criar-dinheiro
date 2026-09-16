"""
AME - Database Layer
SQLAlchemy 2.0 + Async + Sync compatibility + Migrations helpers
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
import os

# Sync engine (para scripts, seeds, jobs)
SYNC_URL = settings.database_url
if SYNC_URL.startswith("sqlite"):
    sync_engine = create_engine(SYNC_URL, connect_args={"check_same_thread": False}, echo=settings.ame_debug == False)
else:
    sync_engine = create_engine(SYNC_URL, echo=False)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async engine (para FastAPI)
ASYNC_URL = settings.database_url_async
if ASYNC_URL.startswith("sqlite"):
    async_engine = create_async_engine(ASYNC_URL, echo=False, connect_args={"check_same_thread": False})
else:
    async_engine = create_async_engine(ASYNC_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

def get_db():
    """Sync dependency"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Async dependency"""
    async with AsyncSessionLocal() as session:
        yield session

def init_db():
    """Cria todas as tabelas (sync) - usado em dev/seed"""
    # Import models to register with Base
    import app.models.base  # noqa: F401
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Database initialized:", SYNC_URL)

def drop_db():
    import app.models.base  # noqa: F401
    Base.metadata.drop_all(bind=sync_engine)
    print("🗑️ Database dropped")

if __name__ == "__main__":
    init_db()
