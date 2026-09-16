"""
AME - ORCHESTRATOR_AGENT
Cérebro do sistema. Avalia situação financeira, oportunidades, tasks, experimentos, desempenho, falhas, recursos, custo, prioridade
Seleciona automaticamente quais agentes precisam trabalhar.
Opera em loop: OBSERVE -> RESEARCH -> DISCOVER -> VALIDATE -> DECIDE -> BUILD -> PUBLISH -> DISTRIBUTE -> SELL -> MEASURE -> LEARN -> OPTIMIZE -> REINVEST -> REPEAT
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
from app.core.observability import logger, metrics_store
from app.core.economic import economic_engine, SurvivalMode
from app.core.experiment import experiment_engine, ExperimentStatus
from app.core.memory import memory_store
from app.core.events import event_bus, EventType, Event

class LoopPhase(str, Enum):
    OBSERVE = "OBSERVE"
    RESEARCH = "RESEARCH"
    DISCOVER = "DISCOVER"
    VALIDATE = "VALIDATE"
    DECIDE = "DECIDE"
    BUILD = "BUILD"
    PUBLISH = "PUBLISH"
    DISTRIBUTE = "DISTRIBUTE"
    SELL = "SELL"
    MEASURE = "MEASURE"
    LEARN = "LEARN"
    OPTIMIZE = "OPTIMIZE"
    REINVEST = "REINVEST"
    REPEAT = "REPEAT"

class Orchestrator:
    def __init__(self):
        self.current_phase = LoopPhase.OBSERVE
        self.cycle_count = 0
        self.is_running = False
        self.paused = False
        self.tasks_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.agents_registry: Dict[str, Any] = {}
        self.last_decision: Optional[Dict[str, Any]] = None

    def register_agent(self, name: str, agent_instance):
        self.agents_registry[name] = agent_instance
        logger.info("agent_registered", agent=name)

    def evaluate_situation(self) -> Dict[str, Any]:
        """Avalia situação geral para decidir próximo passo"""
        econ = economic_engine.get_dashboard()
        exp_stats = experiment_engine.stats()
        mem_stats = memory_store.stats()

        # Prioridade baseada em regras do prompt #39
        priorities = []

        # 1. corrigir falhas críticas
        failed_exps = exp_stats["by_status"].get("FAILED", 0)
        if failed_exps > 0:
            priorities.append({"priority": 1, "action": "analisar_falhas", "reason": f"{failed_exps} experimentos falharam"})

        # 2. garantir estabilidade (health)
        if econ["mode"] == SurvivalMode.EMERGENCY.value:
            priorities.append({"priority": 1, "action": "emergency_preserve_cash", "reason": f"Runway {econ['runway_days']} dias - EMERGENCY"})

        # 3. garantir segurança
        # 4. garantir fluxo de receita
        if econ["revenue"] == 0 and exp_stats["total"] == 0:
            priorities.append({"priority": 2, "action": "descobrir_oportunidade", "reason": "Sem receita e sem experimentos"})

        # 5. validar oportunidades
        if exp_stats["by_status"].get("IDEA", 0) > 0:
            priorities.append({"priority": 3, "action": "validar_oportunidades", "reason": f"{exp_stats['by_status']['IDEA']} ideias para validar"})

        # 6. otimizar conversão
        live = exp_stats["by_status"].get("LIVE", 0)
        if live > 0:
            priorities.append({"priority": 4, "action": "otimizar_live", "reason": f"{live} experimentos LIVE"})

        # 7. reduzir custo
        if econ["mode"] in [SurvivalMode.SURVIVAL.value, SurvivalMode.EMERGENCY.value]:
            priorities.append({"priority": 5, "action": "reduzir_custo", "reason": f"Modo {econ['mode']}"})

        # 8. expandir
        if exp_stats["winners"] > 0 and econ["mode"] == SurvivalMode.GROW.value:
            priorities.append({"priority": 6, "action": "escalar_vencedores", "reason": f"{exp_stats['winners']} vencedores em modo GROW"})

        if not priorities:
            priorities.append({"priority": 7, "action": "discover_nova_oportunidade", "reason": "Operação estável, buscar crescimento"})

        # Ordena por prioridade
        priorities.sort(key=lambda x: x["priority"])

        situation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "economic": econ,
            "experiments": exp_stats,
            "memory": mem_stats,
            "priorities": priorities,
            "next_action": priorities[0] if priorities else None,
            "cycle": self.cycle_count,
            "phase": self.current_phase.value,
        }
        self.last_decision = situation
        return situation

    def decide_agents_to_run(self, situation: Dict[str, Any]) -> List[str]:
        """Seleciona agentes necessários baseado na situação (não rodar todos desnecessariamente)"""
        next_action = situation.get("next_action", {}).get("action", "")
        
        mapping = {
            "descobrir_oportunidade": ["market_agent", "trend_agent", "competitor_agent"],
            "validar_oportunidades": ["validation_agent", "economic_agent", "pricing_agent"],
            "analisar_falhas": ["analytics_agent", "learning_agent", "risk_agent"],
            "emergency_preserve_cash": ["cfo_agent", "economic_agent", "risk_agent"],
            "otimizar_live": ["analytics_agent", "seo_agent", "social_agent", "cfo_agent"],
            "reduzir_custo": ["cfo_agent", "economic_agent"],
            "escalar_vencedores": ["product_builder_agent", "copy_agent", "social_agent", "ads_agent", "sales_agent"],
            "discover_nova_oportunidade": ["market_agent", "trend_agent"],
        }

        agents = mapping.get(next_action, ["market_agent", "validation_agent"])
        
        # Sempre inclui orchestrator e analytics para learning
        if "analytics_agent" not in agents:
            agents.append("analytics_agent")

        # Filtra apenas agentes registrados e respeita survival mode
        available = [a for a in agents if a in self.agents_registry]
        
        # Em SURVIVAL/EMERGENCY, evita agentes caros
        if economic_engine.mode in [SurvivalMode.SURVIVAL, SurvivalMode.EMERGENCY]:
            expensive = {"video_agent", "image_agent", "ads_agent"}
            available = [a for a in available if a not in expensive]
            logger.warning("survival_filter_agents", original=agents, filtered=available, mode=economic_engine.mode.value)

        logger.info("agents_selected", action=next_action, agents=available)
        return available

    async def run_cycle(self):
        """Executa um ciclo completo do loop"""
        self.cycle_count += 1
        logger.info("orchestrator_cycle_start", cycle=self.cycle_count, phase=self.current_phase.value)
        
        # FASE ATUAL: OBSERVE
        situation = self.evaluate_situation()
        logger.info("situation_evaluated", situation=situation)
        
        # Decide agentes
        agents_to_run = self.decide_agents_to_run(situation)
        
        # Executa agentes selecionados
        results = {}
        for agent_name in agents_to_run:
            agent = self.agents_registry.get(agent_name)
            if not agent:
                continue
            try:
                logger.info("agent_executing", agent=agent_name, cycle=self.cycle_count)
                # Cada agente tem método .run()
                if hasattr(agent, "run"):
                    if asyncio.iscoroutinefunction(agent.run):
                        result = await agent.run(context=situation)
                    else:
                        result = agent.run(context=situation)
                else:
                    result = {"status": "no_run_method"}
                
                results[agent_name] = result
                # Registra na memória
                memory_store.add(
                    category="system_memory",
                    action=f"agent:{agent_name} cycle:{self.cycle_count}",
                    result=str(result)[:500],
                    metric={"cycle": self.cycle_count},
                    lesson=result.get("lesson", "") if isinstance(result, dict) else "",
                    next_action=result.get("next_action", "") if isinstance(result, dict) else ""
                )
                
                # Evento
                from app.core.events import emit, EventType
                emit(EventType.AgentTaskCompleted, {"agent": agent_name, "result": result}, source="orchestrator")
                
            except Exception as e:
                logger.error("agent_failed", agent=agent_name, error=str(e))
                results[agent_name] = {"error": str(e)}
                memory_store.add(category="failure_memory", action=f"agent:{agent_name}", result=f"failed: {e}", lesson=str(e))
                try:
                    from app.core.events import emit, EventType
                    emit(EventType.AgentTaskFailed, {"agent": agent_name, "error": str(e)}, source="orchestrator")
                except:
                    pass

        # Avança fase do loop
        phases = list(LoopPhase)
        current_idx = phases.index(self.current_phase)
        self.current_phase = phases[(current_idx + 1) % len(phases)]
        
        # Avalia experimentos
        experiment_engine.evaluate_all()
        
        cycle_result = {
            "cycle": self.cycle_count,
            "phase": self.current_phase.value,
            "situation": situation,
            "agents_run": agents_to_run,
            "results": results,
            "economic": economic_engine.get_dashboard(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.completed_tasks.append(cycle_result)
        if len(self.completed_tasks) > 100:
            self.completed_tasks = self.completed_tasks[-100:]
        
        logger.info("orchestrator_cycle_end", cycle=self.cycle_count, next_phase=self.current_phase.value)
        return cycle_result

    async def start_loop(self, interval_seconds: int = 60, max_cycles: Optional[int] = None):
        """Loop contínuo autônomo"""
        self.is_running = True
        logger.info("orchestrator_loop_started", interval=interval_seconds, max_cycles=max_cycles)
        cycles = 0
        while self.is_running:
            if self.paused:
                await asyncio.sleep(5)
                continue
            try:
                await self.run_cycle()
                cycles += 1
                if max_cycles and cycles >= max_cycles:
                    logger.info("orchestrator_max_cycles_reached", cycles=cycles)
                    break
            except Exception as e:
                logger.error("orchestrator_cycle_error", error=str(e))
            await asyncio.sleep(interval_seconds)
        self.is_running = False

    def pause(self):
        self.paused = True
        logger.info("orchestrator_paused")

    def resume(self):
        self.paused = False
        logger.info("orchestrator_resumed")

    def stop(self):
        self.is_running = False
        logger.info("orchestrator_stopped")

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "paused": self.paused,
            "cycle_count": self.cycle_count,
            "current_phase": self.current_phase.value,
            "agents_registered": list(self.agents_registry.keys()),
            "last_decision": self.last_decision,
            "queue_size": len(self.tasks_queue),
            "completed": len(self.completed_tasks),
        }

# Singleton
orchestrator = Orchestrator()
