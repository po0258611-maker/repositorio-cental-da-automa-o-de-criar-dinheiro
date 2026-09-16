"""
FINANCE AGENTS: CFO, ECONOMIC, PRICING
"""
from app.agents.base import BaseAgent
from typing import Dict, Any
from app.core.economic import economic_engine

class CfoAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="cfo_agent", display_name="CFO_AGENT", category="FINANCE", description="Controla caixa, runway, budget, alocação, survival mode")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        dash = economic_engine.get_dashboard()
        # Recomendações baseadas no modo
        if dash["mode"] == "EMERGENCY":
            rec = "CORTAR tudo não essencial, pausar ads, focar orgânico, vender estoque"
        elif dash["mode"] == "SURVIVAL":
            rec = "Reduzir AI calls caras, priorizar produtos vencedores, reduzir budget 50%"
        elif dash["mode"] == "GROW":
            rec = "Reinvestir 30% do lucro em vencedores, escalar ads, criar upsell"
        else:
            rec = "Manter operação, testar 1 novo experimento/semana"
        report = {
            "dashboard": dash,
            "recomendacao": rec,
            "budget_disponivel": dash["balance"] * 0.2,
            "alerta": "Runway baixo!" if dash["runway_days"] < 7 else "OK"
        }
        self.remember("cfo", f"Modo {dash['mode']} runway {dash['runway_days']} dias", lesson=rec, metric=dash)
        return {"cfo": report, "lesson": rec}

class EconomicAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="economic_agent", display_name="ECONOMIC_AGENT", category="FINANCE", description="Calcula CAC, LTV, ROI, ROAS, margem, pricing")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Exemplo cálculo com dados do context ou defaults
        cac = economic_engine.calculate_cac(marketing_spend=200, new_customers=12)
        ltv = economic_engine.calculate_ltv(avg_purchase_value=97, purchase_frequency=1.2, gross_margin=0.7, avg_customer_lifespan_months=6)
        roas = economic_engine.calculate_roas(revenue=1164, ad_spend=200)
        metrics = {"cac": round(cac,2), "ltv": round(ltv,2), "roas": round(roas,2), "ltv_cac_ratio": round(ltv/cac,2) if cac else 0, "payback": "bom" if ltv/cac > 3 else "ruim"}
        self.remember("economic", f"CAC R${cac:.2f} LTV R${ltv:.2f} ROAS {roas:.2f}", lesson="LTV/CAC >3 é saudável, <1 é prejuízo", metric=metrics)
        return {"metrics": metrics, "lesson": f"LTV/CAC {metrics['ltv_cac_ratio']} - {'Escalar' if metrics['ltv_cac_ratio']>3 else 'Otimizar funil'}"}

class PricingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="pricing_agent", display_name="PRICING_AGENT", category="FINANCE", description="Define e otimiza preços, testes A/B, psicologia de preço")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from app.core.llm_router import llm_router
        prompt = "Sugira 3 estratégias de preço para ebook R$97: âncora, parcelado, bônus. Teste A/B recomendado."
        suggestion = llm_router.generate(prompt, task_type="simple", max_tokens=400)
        pricing = {
            "preco_atual": 97,
            "testes": [
                {"preco": 67, "estrategia": "Volume", "margem": "menor, mais vendas"},
                {"preco": 97, "estrategia": "Equilíbrio atual", "margem": "ideal"},
                {"preco": 147, "estrategia": "Premium com bônus", "margem": "maior, menos vendas"},
            ],
            "recomendacao": "Manter R$97 + teste R$67 como downsell",
            "psicologia": "R$97 (menos que R$100) + 12x R$9,70",
            "raw": suggestion[:400]
        }
        self.remember("pricing", "Teste A/B R$67 vs R$97 vs R$147", lesson="Preço psicológico 97 + parcelamento aumenta conversão 12%")
        return {"pricing": pricing, "lesson": "Testar R$67 como downsell para recuperar carrinho"}

