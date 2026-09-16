"""
RESEARCH AGENTS: MARKET, TREND, COMPETITOR, VALIDATION
"""
from app.agents.base import BaseAgent
from typing import Dict, Any
import random
from app.core.llm_router import llm_router
from app.core.tools import tool_registry
from app.core.events import emit, EventType

class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="market_agent", display_name="MARKET_AGENT", category="RESEARCH", description="Pesquisa de mercado, nichos, problemas, demandas")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Usa LLM Router para gerar oportunidades
        prompt = "Liste 3 nichos emergentes no Brasil com alta demanda e baixa concorrência para produtos digitais em 2026. Para cada: problema, público, tamanho mercado, ticket médio."
        text = llm_router.generate(prompt, task_type="medium", max_tokens=600)
        opportunities = [
            {"nicho": "Produtividade para autônomos", "problema": "Gestão de tempo", "publico": "MEI", "score": 85},
            {"nicho": "IA para pequenos negócios", "problema": "Automatizar atendimento", "publico": "Lojas locais", "score": 92},
            {"nicho": "Saúde mental corporativa", "problema": "Burnout", "publico": "RH empresas", "score": 78},
        ]
        # Simula descoberta via ferramenta web_search
        search_tool = tool_registry.get("web_search")
        if search_tool:
            await search_tool.execute(query="nichos lucrativos 2026 Brasil", limit=3)
        emit(EventType.OpportunityFound, {"agent": self.name, "opportunities": opportunities, "raw_llm": text[:500]}, source=self.name)
        self.remember("market_research", f"Found {len(opportunities)} opportunities", lesson="Nichos de IA para PMEs com maior score", metric={"opportunities": len(opportunities)})
        return {"opportunities": opportunities, "llm_text": text[:800], "lesson": "Priorizar nicho IA para pequenos negócios (score 92)"}

class TrendAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="trend_agent", display_name="TREND_AGENT", category="RESEARCH", description="Monitora tendências, google trends, tiktok, etc")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        trends = [
            {"trend": "Automação com IA sem código", "volume": "+340%", "source": "Google Trends", "oportunidade": "Curso n8n + IA"},
            {"trend": "PLR com IA", "volume": "+210%", "source": "TikTok", "oportunidade": "Pack PLR automatizado"},
            {"trend": "Renda extra com Shopee Afiliado", "volume": "+180%", "source": "YouTube", "oportunidade": "Guia afiliado shopee"},
        ]
        self.remember("trend_analysis", f"{len(trends)} trends", lesson="Automação sem código em alta, criar produto rápido", metric={"trends": len(trends)})
        return {"trends": trends, "lesson": "Apostar em automação sem código + IA"}

class CompetitorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="competitor_agent", display_name="COMPETITOR_AGENT", category="RESEARCH", description="Analisa concorrentes, preços, ofertas")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        competitors = [
            {"concorrente": "Curso X de IA", "preco": 197, "avaliacao": 4.6, "pontos_fracos": "Sem suporte", "oportunidade": "Oferecer suporte + templates"},
            {"concorrente": "Pack Y PLR", "preco": 67, "avaliacao": 4.2, "pontos_fracos": "Conteúdo genérico", "oportunidade": "PLR nichado com IA"},
        ]
        prompt = f"Analise concorrentes {competitors} e sugira diferencial competitivo"
        analysis = llm_router.generate(prompt, task_type="simple", max_tokens=400)
        self.remember("competitor_analysis", f"{len(competitors)} concorrentes", lesson="Diferencial: suporte + nicho + templates prontos")
        return {"competitors": competitors, "analysis": analysis[:600], "lesson": "Diferencial será suporte e nicho específico"}

class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="validation_agent", display_name="VALIDATION_AGENT", category="RESEARCH", description="Valida demanda, concorrência, preço, monetização, MVP, teste de oferta/canal")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Simula validação com scoring
        opportunity = context.get("opportunity") or {"nicho": "IA para pequenos negócios", "score": 92}
        validation = {
            "demanda": random.randint(70, 95),
            "concorrencia": random.randint(30, 60),  # menor é melhor
            "preco_viavel": 97,
            "monetizacao": "venda direta + upsell templates",
            "mvp_sugerido": "Ebook + 5 templates n8n",
            "canal_teste": "Instagram Reels + Telegram",
            "score_final": 88,
            "recomendacao": "GO" if random.random() > 0.2 else "NO-GO",
        }
        if validation["recomendacao"] == "GO":
            emit(EventType.OpportunityValidated, {"opportunity": opportunity, "validation": validation}, source=self.name)
            from app.core.experiment import experiment_engine
            exp = experiment_engine.create(
                name=f"Validar {opportunity.get('nicho','produto')}",
                hypothesis=f"Existe demanda pagante para {opportunity.get('nicho')} a R$ {validation['preco_viavel']}",
                product=validation["mvp_sugerido"],
                channel=validation["canal_teste"],
                budget=50,
                kpi="vendas",
            )
            validation["experiment_id"] = exp.id
        self.remember("validation", f"Validacao {validation['recomendacao']} score {validation['score_final']}", lesson=f"Recomendacao {validation['recomendacao']}", metric=validation)
        return {"validation": validation, "lesson": f"Validação {validation['recomendacao']} - MVP: {validation['mvp_sugerido']}"}
