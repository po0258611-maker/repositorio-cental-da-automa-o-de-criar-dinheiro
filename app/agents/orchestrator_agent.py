from app.agents.base import BaseAgent
from typing import Dict, Any
from app.core.orchestrator import orchestrator
from app.core.observability import logger

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="orchestrator_agent", display_name="ORCHESTRATOR_AGENT", category="CORE", description="Cérebro: estado geral, planejamento, priorização, distribuição, decisão do próximo ciclo")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        status = orchestrator.get_status()
        situation = orchestrator.evaluate_situation()
        logger.info("orchestrator_agent_execute", situation=situation)
        return {
            "status": "ok",
            "orchestrator_status": status,
            "next_action": situation.get("next_action"),
            "economic": situation.get("economic"),
            "lesson": "Orchestrator avaliou situação e priorizou próxima ação",
            "next_agent_suggestion": orchestrator.decide_agents_to_run(situation)
        }
