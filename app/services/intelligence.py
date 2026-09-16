"""
INTELLIGENCE SERVICE: monitora receita, despesas, lucro, margem, CAC, LTV, ROI, ROAS, conversão, retenção, custo IA, operacional, runway
"""
from typing import Dict, Any
from app.core.observability import logger
from app.core.economic import economic_engine
from app.core.experiment import experiment_engine
from app.core.memory import memory_store

class IntelligenceService:
    async def analyze(self) -> Dict[str, Any]:
        logger.info("intelligence_analyze_start")
        from app.agents import AGENTS
        analytics = await AGENTS["analytics_agent"].run(context={})
        cfo = await AGENTS["cfo_agent"].run(context={})
        risk = await AGENTS["risk_agent"].run(context={})
        learning = await AGENTS["learning_agent"].run(context={})
        econ = economic_engine.get_dashboard()
        exp_stats = experiment_engine.stats()
        
        report = {
            "economic": econ,
            "experiments": exp_stats,
            "analytics": analytics.get("metrics"),
            "cfo": cfo.get("cfo"),
            "risk": risk.get("risks"),
            "risk_level": risk.get("level"),
            "learning": learning.get("learning"),
            "insights": analytics.get("insights"),
            "mode": econ["mode"],
            "recommendation": cfo.get("cfo",{}).get("recomendacao") if isinstance(cfo.get("cfo"), dict) else cfo.get("lesson")
        }
        logger.info("intelligence_done", mode=report["mode"])
        return report

    def get_kpis(self) -> Dict[str, Any]:
        return economic_engine.get_dashboard()

intelligence_service = IntelligenceService()
