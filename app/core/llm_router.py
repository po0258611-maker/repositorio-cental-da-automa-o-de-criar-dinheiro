"""
AME - AI Model Router
Abstração para múltiplos LLMs com seleção por custo/qualidade/latência/complexidade
Nunca depender de um só fornecedor
"""
from typing import Optional, Dict, Any, List
from enum import Enum
import os
import time
from app.core.config import settings
from app.core.observability import logger

class TaskComplexity(str, Enum):
    SIMPLE = "simple"      # barato
    MEDIUM = "medium"
    COMPLEX = "complex"    # poderoso
    FAST = "fast"          # baixa latência

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"
    MOCK = "mock"

# Custos aproximados por 1k tokens (USD) - atualização 2024
MODEL_COSTS = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "provider": LLMProvider.OPENAI, "quality": 7, "latency": 0.8},
    "gpt-4o": {"input": 0.0025, "output": 0.01, "provider": LLMProvider.OPENAI, "quality": 10, "latency": 1.2},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015, "provider": LLMProvider.ANTHROPIC, "quality": 10, "latency": 1.5},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003, "provider": LLMProvider.GEMINI, "quality": 7, "latency": 0.5},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005, "provider": LLMProvider.GEMINI, "quality": 9, "latency": 1.0},
    "llama-3.1-70b": {"input": 0.00059, "output": 0.00079, "provider": LLMProvider.GROQ, "quality": 8, "latency": 0.6},
}

class LLMRouter:
    def __init__(self):
        self.daily_cost = 0.0
        self.daily_requests = 0
        self.last_reset_day = time.strftime("%Y-%m-%d")
        self.provider_status = {p: True for p in LLMProvider}

    def _check_daily_reset(self):
        today = time.strftime("%Y-%m-%d")
        if today != self.last_reset_day:
            self.daily_cost = 0.0
            self.daily_requests = 0
            self.last_reset_day = today

    def _check_budget(self, estimated_cost: float) -> bool:
        self._check_daily_reset()
        if self.daily_cost + estimated_cost > settings.max_daily_ai_cost_usd:
            logger.warning("ai_budget_exceeded", daily_cost=self.daily_cost, estimated=estimated_cost, limit=settings.max_daily_ai_cost_usd)
            return False
        return True

    def select_model(self, task_type: TaskComplexity = TaskComplexity.SIMPLE, preferred_provider: Optional[LLMProvider] = None, max_cost: Optional[float] = None) -> str:
        self._check_daily_reset()
        # Lógica de seleção
        if task_type == TaskComplexity.SIMPLE:
            candidates = ["gpt-4o-mini", "gemini-1.5-flash", "llama-3.1-70b"]
        elif task_type == TaskComplexity.FAST:
            candidates = ["gemini-1.5-flash", "llama-3.1-70b", "gpt-4o-mini"]
        elif task_type == TaskComplexity.MEDIUM:
            candidates = ["gpt-4o-mini", "gemini-1.5-pro", "claude-3-5-sonnet"]
        else: # COMPLEX
            candidates = ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"]

        # Filtra por provider preferido
        if preferred_provider:
            candidates = [m for m in candidates if MODEL_COSTS[m]["provider"] == preferred_provider] or candidates

        # Filtra por custo e disponibilidade
        for model in candidates:
            cost = MODEL_COSTS[model]
            if max_cost and cost["input"] > max_cost:
                continue
            provider = cost["provider"]
            # Verifica se tem API key
            has_key = {
                LLMProvider.OPENAI: bool(settings.openai_api_key),
                LLMProvider.ANTHROPIC: bool(settings.anthropic_api_key),
                LLMProvider.GEMINI: bool(settings.gemini_api_key),
                LLMProvider.GROQ: bool(settings.groq_api_key),
            }.get(provider, False)
            # Se não tem key, ainda permite mas vai cair no mock
            if self.provider_status[provider]:
                return model
        return candidates[0]

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        costs = MODEL_COSTS.get(model, {"input": 0.001, "output": 0.002})
        return (input_tokens / 1000) * costs["input"] + (output_tokens / 1000) * costs["output"]

    def generate(self, prompt: str, task_type: str = "simple", max_tokens: int = 500, model: Optional[str] = None, system: Optional[str] = None) -> str:
        complexity = TaskComplexity(task_type) if task_type in [e.value for e in TaskComplexity] else TaskComplexity.SIMPLE
        chosen_model = model or self.select_model(complexity)
        estimated = self.estimate_cost(chosen_model, len(prompt)//4, max_tokens)
        
        if not self._check_budget(estimated):
            logger.warning("ai_budget_blocked", model=chosen_model, estimated=estimated)
            return self._mock_generate(prompt, reason="budget_exceeded")

        # Tenta provider real, fallback para mock
        try:
            result = self._call_provider(chosen_model, prompt, max_tokens, system)
            # Registra custo real estimado
            actual_cost = self.estimate_cost(chosen_model, len(prompt)//4, len(result)//4)
            self.daily_cost += actual_cost
            self.daily_requests += 1
            logger.info("llm_generate", model=chosen_model, cost=actual_cost, daily_cost=self.daily_cost)
            # Atualiza métricas
            from app.core.observability import AI_COST_GAUGE
            AI_COST_GAUGE.set(self.daily_cost)
            return result
        except Exception as e:
            logger.error("llm_provider_failed", model=chosen_model, error=str(e))
            self.provider_status[MODEL_COSTS[chosen_model]["provider"]] = False
            # Fallback para mock
            return self._mock_generate(prompt, reason=f"provider_failed:{e}")

    def _call_provider(self, model: str, prompt: str, max_tokens: int, system: Optional[str]) -> str:
        provider = MODEL_COSTS[model]["provider"]
        
        if provider == LLMProvider.OPENAI and settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(model=model if model.startswith("gpt") else "gpt-4o-mini", messages=messages, max_tokens=max_tokens, temperature=0.7)
            return resp.choices[0].message.content
        
        if provider == LLMProvider.ANTHROPIC and settings.anthropic_api_key:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            msg = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=max_tokens, system=system or "", messages=[{"role": "user", "content": prompt}])
            return msg.content[0].text

        if provider == LLMProvider.GEMINI and settings.gemini_api_key:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            m = genai.GenerativeModel(model if "gemini" in model else "gemini-1.5-flash")
            full_prompt = (system + "\n\n" + prompt) if system else prompt
            resp = m.generate_content(full_prompt, generation_config={"max_output_tokens": max_tokens})
            return resp.text

        # Se não tem key ou provider não configurado, levanta para cair no mock
        raise Exception(f"No API key for {provider} / model {model}")

    def _mock_generate(self, prompt: str, reason: str = "mock") -> str:
        # Geração mock inteligente baseada no prompt
        lower = prompt.lower()
        if "copy" in lower or "venda" in lower:
            return f"[MOCK {reason}] 🔥 Copy gerada para: {prompt[:80]}... \n\nHeadline: Transforme sua vida em 7 dias!\nCTA: Garanta agora com desconto!"
        if "post" in lower or "conteúdo" in lower or "reels" in lower:
            return f"[MOCK {reason}] Post viral sobre: {prompt[:60]}... | Gancho: Você não vai acreditar! | CTA: Comenta EU QUERO"
        if "produto" in lower or "ebook" in lower:
            return f"[MOCK {reason}] 📘 Produto: Guia Completo baseado em '{prompt[:60]}' - 10 capítulos, capa, bônus, pronto para venda."
        return f"[MOCK {reason}] Resposta simulada para: {prompt[:100]}... (Configure OPENAI_API_KEY para geração real)"

    def get_stats(self) -> Dict[str, Any]:
        return {
            "daily_cost": round(self.daily_cost, 4),
            "daily_requests": self.daily_requests,
            "limit": settings.max_daily_ai_cost_usd,
            "remaining": round(settings.max_daily_ai_cost_usd - self.daily_cost, 4),
            "providers": {p.value: self.provider_status[p] for p in LLMProvider},
        }

# Singleton
llm_router = LLMRouter()
