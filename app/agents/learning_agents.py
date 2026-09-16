"""
LEARNING AGENTS: ANALYTICS, EXPERIMENT, LEARNING
"""
from app.agents.base import BaseAgent
from typing import Dict, Any
from app.core.experiment import experiment_engine
from app.core.memory import memory_store
from app.core.observability import logger

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="analytics_agent", display_name="ANALYTICS_AGENT", category="LEARNING", description="Coleta, analisa métricas, conversão, funil, CAC, ROAS")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Simula coleta de métricas de campanhas
        metrics = {
            "impressoes": 15400,
            "cliques": 890,
            "ctr": 5.78,
            "leads": 134,
            "cpl": 1.49,
            "vendas": 18,
            "conversao": 13.43,  # leads->vendas
            "receita": 1746,
            "cac": 11.11,
            "roas": 8.73,
        }
        # Insights
        insights = []
        if metrics["ctr"] > 3:
            insights.append("CTR excelente (>3%) - criativo vencedor")
        if metrics["conversao"] > 10:
            insights.append("Conversão alta - escalar")
        else:
            insights.append("Conversão baixa - otimizar checkout")
        if metrics["roas"] > 3:
            insights.append(f"ROAS {metrics['roas']} - lucrativo, escalar budget 20%")
        
        self.remember("analytics", f"ROAS {metrics['roas']} CTR {metrics['ctr']}%", lesson=" | ".join(insights), metric=metrics)
        return {"metrics": metrics, "insights": insights, "lesson": " | ".join(insights)}

class ExperimentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="experiment_agent", display_name="EXPERIMENT_AGENT", category="LEARNING", description="Gerencia ciclo de vida de experimentos, cria, avalia, arquiva")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        stats = experiment_engine.stats()
        # Avalia todos
        experiment_engine.evaluate_all()
        # Cria novo se não tem LIVE
        live = [e for e in experiment_engine.list() if e.status.value == "LIVE"]
        if not live and stats["total"] < 5:
            exp = experiment_engine.create(
                name="Teste Tripwire R$27 vs R$97",
                hypothesis="Tripwire R$27 aumenta conversão inicial em 40%",
                product="Ebook IA",
                channel="Instagram Ads",
                budget=30,
                kpi="conversão",
            )
            exp.transition(exp.status.__class__.VALIDATING, "Criado pelo ExperimentAgent")
            stats = experiment_engine.stats()
            self.remember("experiment", f"Criado {exp.id}", lesson="Manter pipeline de experimentos sempre com 1 LIVE")
            return {"stats": stats, "new_experiment": exp.to_dict(), "lesson": "Novo experimento criado, mover para LIVE em 24h"}
        self.remember("experiment", f"Stats {stats}", lesson="Avaliar experimentos diariamente", metric=stats)
        return {"stats": stats, "lesson": "Experimentos avaliados, manter 1 LIVE sempre"}

class LearningAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="learning_agent", display_name="LEARNING_AGENT", category="LEARNING", description="Aprende com sucessos/fracassos, atualiza memória, evita repetir erro")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        failures = memory_store.get_failures(limit=5)
        successes = memory_store.get_successes(limit=5)
        # Extrai lições
        lessons = []
        if failures:
            lessons.append(f"Evitar: {failures[0]['action']} - {failures[0]['lesson']}")
        if successes:
            lessons.append(f"Replicar: {successes[0]['action']} - {successes[0]['lesson']}")
        
        # Verifica se deve evitar repetição
        avoid = memory_store.should_avoid("ads com budget alto em SURVIVAL")
        
        # Atualiza experiment_memory
        recent = memory_store.query(limit=3)
        
        summary = {
            "total_memories": memory_store.stats()["total"],
            "failures": len(failures),
            "successes": len(successes),
            "lessons": lessons,
            "should_avoid_ads_survival": avoid,
            "recent": recent[:2]
        }
        self.remember("learning", f"{len(lessons)} lessons", lesson=" | ".join(lessons) if lessons else "Primeiro ciclo, sem histórico", metric={"failures": len(failures), "successes": len(successes)})
        return {"learning": summary, "lesson": "Aprender com falhas evita queimar caixa repetindo erro"}
