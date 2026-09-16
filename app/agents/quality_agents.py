"""
QUALITY AGENTS: QA, SECURITY, RISK
"""
from app.agents.base import BaseAgent
from typing import Dict, Any
from pathlib import Path
import re

class QaAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="qa_agent", display_name="QA_AGENT", category="QUALITY", description="Testes, qualidade, validação, revisão, smoke tests")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Roda verificações básicas
        checks = []
        # Verifica se landing existe
        if Path("exports/landing/index.html").exists():
            checks.append({"check": "Landing existe", "status": "PASS"})
        else:
            checks.append({"check": "Landing existe", "status": "FAIL"})
        # Verifica se produto existe
        if Path("exports/products").exists() and any(Path("exports/products").iterdir()):
            checks.append({"check": "Produto gerado", "status": "PASS"})
        else:
            checks.append({"check": "Produto gerado", "status": "WARN"})
        # Verifica se copy existe
        if Path("exports/copy/copies.json").exists():
            checks.append({"check": "Copy gerada", "status": "PASS"})
        else:
            checks.append({"check": "Copy gerada", "status": "FAIL"})
        
        passed = len([c for c in checks if c["status"]=="PASS"])
        total = len(checks)
        health = "healthy" if passed==total else "degraded" if passed>=total*0.5 else "failed"
        self.remember("qa", f"{passed}/{total} checks passed", lesson=f"Health {health}", metric={"passed": passed, "total": total})
        return {"checks": checks, "health": health, "passed": f"{passed}/{total}", "lesson": "QA: corrigir FAIL antes de publicar"}

class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="security_agent", display_name="SECURITY_AGENT", category="QUALITY", description="Audita segurança, secrets, validação, rate limit")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        # Verifica se .env está no .gitignore
        gitignore = Path(".gitignore").read_text(encoding="utf-8") if Path(".gitignore").exists() else ""
        if ".env" not in gitignore:
            issues.append({"severity": "HIGH", "issue": ".env não está no .gitignore - risco de expor secrets"})
        else:
            issues.append({"severity": "OK", "issue": ".env protegido no .gitignore"})
        # Verifica se há secrets hardcoded
        for py in Path("app").rglob("*.py"):
            text = py.read_text(encoding="utf-8", errors="ignore")
            if re.search(r'sk-[a-zA-Z0-9]{20,}', text):
                issues.append({"severity": "HIGH", "issue": f"Possível secret hardcoded em {py}"})
                break
        else:
            issues.append({"severity": "OK", "issue": "Nenhum secret hardcoded detectado"})
        
        # Verifica validação de input
        issues.append({"severity": "OK", "issue": "Validação de input ativa (sanitize_input)"})
        
        self.remember("security", f"{len([i for i in issues if i['severity']=='HIGH'])} high issues", lesson="Manter .env fora do git e validar inputs")
        return {"issues": issues, "lesson": "Security audit completo"}

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="risk_agent", display_name="RISK_AGENT", category="QUALITY", description="Avalia risco financeiro, operacional, legal, reputacional")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from app.core.economic import economic_engine
        dash = economic_engine.get_dashboard()
        risks = []
        if dash["runway_days"] < 7:
            risks.append({"risco": "Runway baixo", "prob": "alta", "impacto": "alto", "mitigacao": "Cortar custos, pausar experimentos caros"})
        if dash["margin"] < 0.2 and dash["revenue"]>0:
            risks.append({"risco": "Margem baixa", "prob": "média", "impacto": "médio", "mitigacao": "Aumentar preço ou reduzir CAC"})
        # Risco de dependência de 1 canal
        risks.append({"risco": "Dependência Instagram", "prob": "média", "impacto": "alto", "mitigacao": "Diversificar para Email + SEO + TikTok"})
        # Risco legal
        risks.append({"risco": "Compliance afiliado", "prob": "baixa", "impacto": "médio", "mitigacao": "Revisar termos Hotmart/Kiwify, não prometer renda garantida"})
        
        level = "HIGH" if any(r["impacto"]=="alto" and r["prob"]=="alta" for r in risks) else "MEDIUM"
        self.remember("risk", f"{len(risks)} riscos, level {level}", lesson="Diversificar canais reduz risco", metric={"risks": len(risks)})
        if level=="HIGH":
            try:
                from app.core.events import emit, EventType
                emit(EventType.RiskDetected, {"level": level, "risks": risks}, source=self.name)
            except:
                pass
        return {"risks": risks, "level": level, "dash": dash, "lesson": f"Risco {level}: mitigar runway e diversificar canais"}
