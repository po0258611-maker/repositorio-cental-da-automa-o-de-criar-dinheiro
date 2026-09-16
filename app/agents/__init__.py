"""
AME - Agents Registry
Registra todos os agentes no Orchestrator
"""
from app.agents.base import BaseAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.research_agents import MarketAgent, TrendAgent, CompetitorAgent, ValidationAgent
from app.agents.product_agents import ProductStrategistAgent, ProductBuilderAgent, DigitalProductAgent, LandingPageAgent
from app.agents.creative_agents import CopyAgent, ImageAgent, VideoAgent, ContentAgent
from app.agents.growth_agents import SeoAgent, SocialAgent, AdsAgent, SalesAgent, EmailAgent
from app.agents.finance_agents import CfoAgent, EconomicAgent, PricingAgent
from app.agents.quality_agents import QaAgent, SecurityAgent, RiskAgent
from app.agents.learning_agents import AnalyticsAgent, ExperimentAgent, LearningAgent

AGENTS = {
    # CORE
    "orchestrator_agent": OrchestratorAgent(),
    # RESEARCH
    "market_agent": MarketAgent(),
    "trend_agent": TrendAgent(),
    "competitor_agent": CompetitorAgent(),
    "validation_agent": ValidationAgent(),
    # PRODUCT
    "product_strategist_agent": ProductStrategistAgent(),
    "product_builder_agent": ProductBuilderAgent(),
    "digital_product_agent": DigitalProductAgent(),
    "landing_page_agent": LandingPageAgent(),
    # CREATIVE
    "copy_agent": CopyAgent(),
    "image_agent": ImageAgent(),
    "video_agent": VideoAgent(),
    "content_agent": ContentAgent(),
    # GROWTH
    "seo_agent": SeoAgent(),
    "social_agent": SocialAgent(),
    "ads_agent": AdsAgent(),
    "sales_agent": SalesAgent(),
    "email_agent": EmailAgent(),
    # FINANCE
    "cfo_agent": CfoAgent(),
    "economic_agent": EconomicAgent(),
    "pricing_agent": PricingAgent(),
    # QUALITY
    "qa_agent": QaAgent(),
    "security_agent": SecurityAgent(),
    "risk_agent": RiskAgent(),
    # LEARNING
    "analytics_agent": AnalyticsAgent(),
    "experiment_agent": ExperimentAgent(),
    "learning_agent": LearningAgent(),
}

def register_all(orchestrator):
    for name, agent in AGENTS.items():
        orchestrator.register_agent(name, agent)
    return AGENTS

__all__ = ["AGENTS", "register_all"]
