"""
PRODUCT AGENTS: STRATEGIST, BUILDER, DIGITAL_PRODUCT, LANDING_PAGE
"""
from app.agents.base import BaseAgent
from typing import Dict, Any
import json
from pathlib import Path
from app.core.llm_router import llm_router
from app.core.events import emit, EventType

class ProductStrategistAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="product_strategist_agent", display_name="PRODUCT_STRATEGIST_AGENT", category="PRODUCT", description="Define estratégia de produto, preço, posicionamento, funil")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Recebe oportunidade validada
        hypothesis = context.get("validation", {}).get("mvp_sugerido", "Ebook IA para negócios")
        prompt = f"Crie estratégia de produto para: {hypothesis}. Defina: nome, preço, bônus, garantia, funil (tripwire, upsell), posicionamento."
        strategy = llm_router.generate(prompt, task_type="complex", max_tokens=700)
        plan = {
            "nome": "IA Prática para Lojas Locais",
            "preco": 97,
            "preco_original": 197,
            "bonus": ["Pack 20 prompts", "5 templates n8n", "Grupo VIP Telegram"],
            "garantia": "7 dias",
            "funil": {"tripwire": "Ebook R$27", "principal": "Curso R$97", "upsell": "Mentoria R$297"},
            "posicionamento": "Sem código, em 7 dias, com celular",
            "raw": strategy[:800]
        }
        emit(EventType.ProductCreated, {"strategy": plan}, source=self.name)
        self.remember("product_strategy", f"Estrategia {plan['nome']}", lesson="Funil tripwire + upsell aumenta LTV", metric={"price": plan["preco"]})
        return {"strategy": plan, "lesson": "Tripwire R$27 para aumentar conversão"}

class ProductBuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="product_builder_agent", display_name="PRODUCT_BUILDER_AGENT", category="PRODUCT", description="Constrói o produto (estrutura, conteúdo, entrega)")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        strategy = context.get("strategy", {"nome": "Produto IA", "preco": 97})
        # Simula criação de produto digital via DocumentProvider
        from app.providers.document_provider import document_provider
        ebook = document_provider.create_ebook(title=strategy["nome"], chapters=["Intro", "Fundamentos IA", "Automação na prática", "Templates", "Venda"], author="AME")
        Path("exports/products").mkdir(parents=True, exist_ok=True)
        out_path = f"exports/products/{strategy['nome'].replace(' ', '_')}.json"
        Path(out_path).write_text(json.dumps(ebook, ensure_ascii=False, indent=2), encoding="utf-8")
        self.remember("product_build", f"Produto {strategy['nome']} criado", lesson="Ebook 5 capítulos + bônus pronto", metric={"chapters": 5})
        emit(EventType.ProductCreated, {"product": strategy["nome"], "path": out_path}, source=self.name)
        return {"product": strategy["nome"], "path": out_path, "ebook": ebook, "lesson": "Produto construído e salvo em exports/products"}

class DigitalProductAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="digital_product_agent", display_name="DIGITAL_PRODUCT_AGENT", category="PRODUCT", description="Gera produtos digitais: PDFs, templates, ferramentas, micro-SaaS")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Gera template/tool adicional
        templates = [
            {"nome": "Planilha CAC/LTV", "tipo": "xlsx", "valor": "R$ 47"},
            {"nome": "Prompt Pack 100 prompts vendas", "tipo": "pdf", "valor": "R$ 67"},
        ]
        for t in templates:
            Path("exports/templates").mkdir(parents=True, exist_ok=True)
            safe = t['nome'].replace(' ', '_').replace('/', '_').replace('\\', '_')
            Path(f"exports/templates/{safe}.txt").write_text(f"Template: {t['nome']} - gerado por AME", encoding="utf-8")
        self.remember("digital_product", f"{len(templates)} templates", lesson="Templates aumentam valor percebido")
        return {"templates": templates, "lesson": "Templates gerados como bônus"}

class LandingPageAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="landing_page_agent", display_name="LANDING_PAGE_AGENT", category="PRODUCT", description="Cria landing pages, sites, checkout")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        strategy = context.get("strategy", {"nome": "IA Prática", "preco": 97})
        prompt = f"Crie copy para landing page de {strategy['nome']} por R$ {strategy['preco']}. Inclua headline, sub, benefícios, prova, CTA, garantia."
        copy = llm_router.generate(prompt, task_type="medium", max_tokens=800)
        html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>{strategy['nome']}</title>
        <style>body{{font-family:system-ui;max-width:700px;margin:40px auto;padding:20px}} .cta{{background:#00d084;color:#000;padding:16px 32px;border-radius:12px;font-weight:800;display:inline-block;text-decoration:none}} </style></head>
        <body><h1>{strategy['nome']}</h1><p>{copy[:500]}</p><a class='cta' href='#checkout'>Quero por R$ {strategy['preco']} - Garantia 7 dias</a></body></html>"""
        Path("exports/landing").mkdir(parents=True, exist_ok=True)
        path = "exports/landing/index.html"
        Path(path).write_text(html, encoding="utf-8")
        emit(EventType.ProductPublished, {"landing": path, "product": strategy["nome"]}, source=self.name)
        self.remember("landing_page", f"LP {strategy['nome']}", lesson="LP com CTA forte e garantia", metric={"price": strategy["preco"]})
        return {"landing_path": path, "copy": copy[:800], "lesson": "Landing publicada em exports/landing/index.html"}
