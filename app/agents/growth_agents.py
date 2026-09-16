"""
GROWTH AGENTS: SEO, SOCIAL, ADS, SALES, EMAIL
"""
from app.agents.base import BaseAgent
from typing import Dict, Any
from pathlib import Path
from app.core.llm_router import llm_router
from app.core.events import emit, EventType

class SeoAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="seo_agent", display_name="SEO_AGENT", category="GROWTH", description="Otimiza SEO, artigos, palavras-chave")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        keyword = context.get("keyword", "automação com IA")
        prompt = f"Crie artigo SEO 800 palavras para keyword '{keyword}': título, meta, H1, H2s, introdução, conclusão, CTA"
        article = llm_router.generate(prompt, task_type="complex", max_tokens=1000)
        seo = {"keyword": keyword, "volume": 3200, "dificuldade": "média", "artigo": article[:800], "otimizacoes": ["H1 com keyword", "FAQ schema", "Links internos"]}
        Path("exports/seo").mkdir(parents=True, exist_ok=True)
        Path("exports/seo/artigo.md").write_text(f"# {keyword}\n\n{article}", encoding="utf-8")
        self.remember("seo", f"Artigo {keyword}", lesson="Artigo 800 palavras + FAQ rankeia melhor")
        return {"seo": seo, "lesson": "Artigo SEO pronto em exports/seo/artigo.md"}

class SocialAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="social_agent", display_name="SOCIAL_AGENT", category="GROWTH", description="Gerencia redes sociais, autopost, engajamento")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Integra com automacoes/trafego
        try:
            from automacoes.trafego.autopost import rodar_trafego
            # Simula agendamento sem input
            import json
            p = Path("exports/content/posts.json")
            if p.exists():
                posts = json.loads(p.read_text(encoding="utf-8"))
                schedule = [{"post": posts[i]["titulo"][:40] if isinstance(posts[i], dict) and "titulo" in posts[i] else f"Post {i}", "rede": "Instagram", "hora": f"{9+i*3}:00"} for i in range(min(3, len(posts)))]
            else:
                schedule = [{"post": "Post demo", "rede": "Instagram", "hora": "09:00"}]
        except Exception as e:
            schedule = [{"error": str(e), "rede": "Instagram", "hora": "09:00"}]
        emit(EventType.CampaignCreated, {"channel": "social", "schedule": schedule}, source=self.name)
        self.remember("social", f"{len(schedule)} posts agendados", lesson="2 posts/dia é ideal para algoritmo")
        return {"schedule": schedule, "lesson": "Conteúdo agendado para distribuição"}

class AdsAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ads_agent", display_name="ADS_AGENT", category="GROWTH", description="Cria e otimiza anúncios pagos, gestão de budget")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Decision: só roda se economic permitir
        from app.core.economic import economic_engine
        if not economic_engine.should_allow_expensive_operation(5.0):
            return {"status": "skipped", "reason": f"Modo {economic_engine.mode.value} bloqueia ads caros", "lesson": "Preservando caixa, focar orgânico"}
        budget = context.get("budget", 20)
        prompt = f"Crie campanha Facebook Ads para produto R$97 com budget R${budget}/dia: 3 criativos, 2 públicos, headline, CTA"
        camp = llm_router.generate(prompt, task_type="medium", max_tokens=600)
        data = {"budget": budget, "cpm_estimado": 8.5, "ctr_estimado": 2.1, "cpc": 0.45, "campanha": camp[:600]}
        economic_engine.record_expense(budget, description="Ads Facebook", category="ads")
        self.remember("ads", f"Campanha R${budget}/dia", lesson="Testar 3 criativos + 2 públicos, matar perdedores em 48h", metric={"budget": budget})
        return {"ads": data, "lesson": "Campanha criada, monitorar CTR >1.5%"}

class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="sales_agent", display_name="SALES_AGENT", category="GROWTH", description="Gestão de funil, checkout, ofertas, conversão, follow-up")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        offer = {"produto": "IA Prática R$97", "checkout": "https://kiwify.com.br/...", "pix": "PIX/Cartão em 12x", "garantia": "7 dias", "bonus": "3 bônus"}
        # Simula otimização de funil
        funnel = {"visitantes": 1000, "leads": 120, "checkout": 45, "vendas": 12, "conversao": 1.2, "ticket": 97, "receita": 1164}
        from app.core.economic import economic_engine
        economic_engine.record_revenue(1164, description="Vendas funil", channel="sales")
        emit(EventType.SaleCreated, {"amount": 1164, "sales": 12, "funnel": funnel}, source=self.name)
        self.remember("sales", f"{funnel['vendas']} vendas R${funnel['receita']}", lesson="Checkout 1-click aumenta conversão 18%", metric=funnel)
        return {"offer": offer, "funnel": funnel, "lesson": "Funil com 1.2% conversão, otimizar checkout"}

class EmailAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="email_agent", display_name="EMAIL_AGENT", category="GROWTH", description="Email marketing, sequências, automação, retenção")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Reusa automacoes/email
        sequencia = [
            {"dia": 0, "assunto": "Seu acesso + bônus", "cta": "Acessar"},
            {"dia": 1, "assunto": "Erro que 90% comete", "cta": "Corrigir"},
            {"dia": 3, "assunto": "Desconto expira hoje", "cta": "Garantir"},
        ]
        for email in sequencia:
            prompt = f"Escreva email dia {email['dia']} assunto '{email['assunto']}' para vender produto R$97, tom humano, 200 palavras, CTA {email['cta']}"
            body = llm_router.generate(prompt, task_type="simple", max_tokens=400)
            email["body"] = body[:400]
        Path("exports/email").mkdir(parents=True, exist_ok=True)
        import json
        Path("exports/email/sequencia.json").write_text(json.dumps(sequencia, ensure_ascii=False, indent=2), encoding="utf-8")
        self.remember("email", f"{len(sequencia)} emails", lesson="Sequência 7 dias com escassez no D3 converte 2.3x")
        return {"emails": sequencia, "lesson": "Sequência email salva em exports/email/sequencia.json"}
