"""
AME - Database Models
All entities: users, agents, tasks, projects, experiments, products, offers, campaigns, leads, customers, sales, transactions, expenses, metrics, events, memory, integrations, api_usage, system_settings
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.core.database import Base

def gen_id():
    return str(uuid.uuid4())[:12]

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False)  # ex: market_agent
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # CORE, RESEARCH, PRODUCT, etc
    is_active = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    last_run = Column(DateTime, nullable=True)
    total_runs = Column(Integer, default=0)
    created_at = Column(DateTime, default=now)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    agent_name = Column(String, ForeignKey("agents.name"), nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    status = Column(String, default="pending")  # pending, running, completed, failed
    priority = Column(Integer, default=5)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    cost = Column(Float, default=0.0)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)
    completed_at = Column(DateTime, nullable=True)

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")  # active, paused, archived
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    name = Column(String, nullable=False)
    hypothesis = Column(Text, nullable=False)
    audience = Column(String, nullable=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=True)
    channel = Column(String, default="organic")
    budget = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    kpi = Column(String, default="conversion")
    status = Column(String, default="IDEA")
    risk = Column(String, default="medium")
    deadline = Column(DateTime, nullable=True)
    metrics = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, default="digital")  # digital, ebook, saas, template, etc
    price = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    status = Column(String, default="draft")  # draft, building, live, archived, winner
    content = Column(JSON, default=dict)  # para ebooks, etc
    assets = Column(JSON, default=dict)  # imagens, etc
    sales_count = Column(Integer, default=0)
    revenue_total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Offer(Base):
    __tablename__ = "offers"
    id = Column(String, primary_key=True, default=gen_id)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount = Column(Float, default=0.0)
    checkout_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    channel = Column(String, nullable=False)  # seo, social, ads, email
    product_id = Column(String, ForeignKey("products.id"), nullable=True)
    experiment_id = Column(String, ForeignKey("experiments.id"), nullable=True)
    status = Column(String, default="draft")  # draft, live, paused, ended
    budget = Column(Float, default=0.0)
    spend = Column(Float, default=0.0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    leads = Column(Integer, default=0)
    sales = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)  # campaign, channel
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    status = Column(String, default="new")  # new, contacted, qualified, converted, lost
    score = Column(Integer, default=0)
    extra_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    ltv = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    first_purchase_at = Column(DateTime, nullable=True)
    last_purchase_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(String, primary_key=True, default=gen_id)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=True)
    offer_id = Column(String, ForeignKey("offers.id"), nullable=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="BRL")
    status = Column(String, default="completed")  # pending, completed, refunded, failed
    payment_method = Column(String, nullable=True)
    funnel_stage = Column(String, nullable=True)
    created_at = Column(DateTime, default=now)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)  # revenue, expense
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    channel = Column(String, nullable=True)
    balance_after = Column(Float, nullable=True)
    extra_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=now)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(String, primary_key=True, default=gen_id)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # ai_cost, ads, operational, etc
    description = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)  # revenue, profit, ctr, conversion, etc
    value = Column(Float, nullable=False)
    dimensions = Column(JSON, default=dict)  # ex: {"channel": "seo", "product": "ebook1"}
    timestamp = Column(DateTime, default=now)

class EventRecord(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)
    payload = Column(JSON, default=dict)
    source = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=now)

class Memory(Base):
    __tablename__ = "memory"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    category = Column(String, nullable=False)  # market_memory, etc
    action = Column(Text, nullable=False)
    result = Column(Text, nullable=False)
    cost = Column(Float, default=0.0)
    metric = Column(JSON, default=dict)
    lesson = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True)
    extra_data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=now)

class Integration(Base):
    __tablename__ = "integrations"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False)  # openai, telegram, stripe, etc
    type = Column(String, nullable=False)  # llm, messaging, payment, etc
    is_active = Column(Boolean, default=False)
    config = Column(JSON, default=dict)  # não armazena secrets em plain, usa env
    last_sync = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now)

class ApiUsage(Base):
    __tablename__ = "api_usage"
    id = Column(String, primary_key=True, default=gen_id)
    provider = Column(String, nullable=False)  # openai, gemini, etc
    endpoint = Column(String, nullable=True)
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

class SystemSettings(Base):
    __tablename__ = "system_settings"
    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=now, onupdate=now)
