"""
AME - Memory System
Memória persistente categorizada para aprendizado contínuo
Categorias: market, product, customer, marketing, financial, experiment, failure, success, system
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json
import uuid
from pathlib import Path
from app.core.observability import logger

MEMORY_CATEGORIES = [
    "market_memory",
    "product_memory",
    "customer_memory",
    "marketing_memory",
    "financial_memory",
    "experiment_memory",
    "failure_memory",
    "success_memory",
    "system_memory",
]

class MemoryEntry:
    def __init__(self, category: str, action: str, result: str, cost: float = 0.0, metric: Optional[Dict] = None, lesson: str = "", next_action: str = "", metadata: Optional[Dict] = None):
        if category not in MEMORY_CATEGORIES:
            raise ValueError(f"Category must be one of {MEMORY_CATEGORIES}")
        self.id = str(uuid.uuid4())[:8]
        self.category = category
        self.action = action
        self.result = result
        self.cost = cost
        self.metric = metric or {}
        self.lesson = lesson
        self.next_action = next_action
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)
        self.embedding = None  # futuro: vetor para busca semântica

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "action": self.action,
            "result": self.result,
            "cost": self.cost,
            "metric": self.metric,
            "lesson": self.lesson,
            "next_action": self.next_action,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

class MemoryStore:
    def __init__(self, persist_path: str = "./ame_memory.json"):
        self.persist_path = Path(persist_path)
        self.entries: List[MemoryEntry] = []
        self.load()

    def add(self, category: str, action: str, result: str, cost: float = 0.0, metric: Optional[Dict] = None, lesson: str = "", next_action: str = "", metadata: Optional[Dict] = None) -> MemoryEntry:
        entry = MemoryEntry(category, action, result, cost, metric, lesson, next_action, metadata)
        self.entries.append(entry)
        logger.info("memory_added", category=category, action=action, lesson=lesson)
        self.save()
        return entry

    def query(self, category: Optional[str] = None, limit: int = 20, contains: Optional[str] = None) -> List[Dict[str, Any]]:
        filtered = self.entries
        if category:
            filtered = [e for e in filtered if e.category == category]
        if contains:
            lower = contains.lower()
            filtered = [e for e in filtered if lower in e.action.lower() or lower in e.lesson.lower() or lower in e.result.lower()]
        # mais recentes primeiro
        filtered = sorted(filtered, key=lambda x: x.timestamp, reverse=True)
        return [e.to_dict() for e in filtered[:limit]]

    def get_failures(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.query(category="failure_memory", limit=limit)

    def get_successes(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.query(category="success_memory", limit=limit)

    def should_avoid(self, action: str) -> bool:
        """Verifica se ação similar já falhou sem nova hipótese"""
        failures = self.query(category="failure_memory", contains=action, limit=5)
        successes = self.query(category="success_memory", contains=action, limit=5)
        # Se tem mais falhas que sucessos recentes, evitar repetição exata
        return len(failures) > len(successes) and len(failures) >= 2

    def save(self):
        try:
            data = [e.to_dict() for e in self.entries[-500:]]  # mantém últimas 500
            self.persist_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error("memory_save_failed", error=str(e))

    def load(self):
        try:
            if self.persist_path.exists():
                data = json.loads(self.persist_path.read_text(encoding="utf-8"))
                for item in data:
                    e = MemoryEntry(
                        category=item["category"],
                        action=item["action"],
                        result=item["result"],
                        cost=item.get("cost", 0),
                        metric=item.get("metric"),
                        lesson=item.get("lesson", ""),
                        next_action=item.get("next_action", ""),
                        metadata=item.get("metadata"),
                    )
                    e.id = item["id"]
                    e.timestamp = datetime.fromisoformat(item["timestamp"])
                    self.entries.append(e)
                logger.info("memory_loaded", count=len(self.entries))
        except Exception as e:
            logger.error("memory_load_failed", error=str(e))

    def stats(self) -> Dict[str, Any]:
        by_cat = {cat: len([e for e in self.entries if e.category == cat]) for cat in MEMORY_CATEGORIES}
        return {
            "total": len(self.entries),
            "by_category": by_cat,
            "last_entry": self.entries[-1].to_dict() if self.entries else None,
        }

# Singleton
memory_store = MemoryStore()

# Helper rápido
def remember(category: str, action: str, result: str, lesson: str = "", **kwargs):
    return memory_store.add(category, action, result, lesson=lesson, **kwargs)
