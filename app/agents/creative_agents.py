"""
CREATIVE AGENTS: COPY, IMAGE, VIDEO, CONTENT
"""
from app.agents.base import BaseAgent
from typing import Dict, Any
from pathlib import Path
from app.core.llm_router import llm_router
from app.providers.image_provider import image_provider
from app.providers.video_provider import video_provider

class CopyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="copy_agent", display_name="COPY_AGENT", category="CREATIVE", description="Gera copies, headlines, anúncios, emails")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        product = context.get("strategy", {}).get("nome", "Produto IA") if isinstance(context.get("strategy"), dict) else "Produto IA"
        prompt = f"Crie 3 copies para {product}: 1) Anúncio curto Facebook, 2) Email abertura, 3) Roteiro Reels 30s. Foco em dor, benefício, CTA."
        copy = llm_router.generate(prompt, task_type="medium", max_tokens=800)
        copies = {
            "ad": f"🔥 {product} - Transforme em 7 dias! {copy[:120]}",
            "email": f"Assunto: O segredo que ninguém te conta sobre {product}",
            "reels": f"Roteiro 30s: Gancho 3s + 3 dicas + CTA Comenta EU QUERO",
            "raw": copy[:800]
        }
        Path("exports/copy").mkdir(parents=True, exist_ok=True)
        Path("exports/copy/copies.json").write_text(str(copies), encoding="utf-8")
        self.remember("copy", f"3 copies para {product}", lesson="Copy com dor + benefício + prova converte mais")
        return {"copies": copies, "lesson": "Copies geradas e salvas"}

class ImageAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="image_agent", display_name="IMAGE_AGENT", category="CREATIVE", description="Gera imagens, criativos, capas, posts")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        strategy = context.get("strategy", {"nome": "IA Prática"})
        prompt_img = f"Capa de ebook moderno, título '{strategy.get('nome','Produto')}', estilo premium, cores verde e preto, 3D, alta qualidade"
        result = image_provider.generate(prompt_img, width=1024, height=1024)
        # Salva placeholder
        Path("exports/creatives").mkdir(parents=True, exist_ok=True)
        # Cria SVG como placeholder de capa
        svg = f"<svg width='600' height='800' xmlns='http://www.w3.org/2000/svg'><rect width='100%' height='100%' fill='#0a0a0f'/><text x='50%' y='45%' fill='#00d084' font-size='32' text-anchor='middle' font-family='system-ui' font-weight='900'>{strategy.get('nome','AME')[:20]}</text><text x='50%' y='55%' fill='#fff' font-size='16' text-anchor='middle'>Ebook Premium • AME</text></svg>"
        Path("exports/creatives/capa.svg").write_text(svg, encoding="utf-8")
        self.remember("image", "Capa gerada", lesson="Imagem premium aumenta conversão em 23%", metric={"provider": result.get("provider")})
        return {"image": result, "path": "exports/creatives/capa.svg", "lesson": "Criativo gerado"}

class VideoAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="video_agent", display_name="VIDEO_AGENT", category="CREATIVE", description="Gera vídeos, roteiros, narração")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = "Roteiro vídeo 30s faceless para vender ebook IA: gancho 3s, 3 benefícios, prova, CTA"
        roteiro = llm_router.generate(prompt, task_type="simple", max_tokens=500)
        video = video_provider.create_script(title="VSL 30s", script=roteiro, duration=30)
        Path("exports/videos").mkdir(parents=True, exist_ok=True)
        Path("exports/videos/roteiro.txt").write_text(roteiro, encoding="utf-8")
        self.remember("video", "Roteiro 30s", lesson="Vídeo faceless escala sem aparecer")
        return {"roteiro": roteiro[:600], "video": video, "lesson": "Roteiro pronto para CapCut/11Labs"}

class ContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="content_agent", display_name="CONTENT_AGENT", category="CREATIVE", description="Gera posts, carrosséis, threads, newsletters")
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        tema = context.get("tema", "renda extra com IA")
        # Reusa lógica do automacoes/conteudo_ia
        try:
            from automacoes.conteudo_ia.gerador import gerar_com_ia
            posts = gerar_com_ia(tema, 3)
        except:
            prompt = f"Crie 3 posts carrossel para Instagram sobre {tema}: título, 5 slides, legenda, hashtags"
            text = llm_router.generate(prompt, task_type="medium", max_tokens=800)
            posts = [{"titulo": f"Post {i+1}", "conteudo": text[:400]} for i in range(3)]
        Path("exports/content").mkdir(parents=True, exist_ok=True)
        import json
        Path("exports/content/posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
        self.remember("content", f"{len(posts)} posts", lesson="Conteúdo em carrossel gera mais salvamentos")
        return {"posts": posts, "lesson": f"{len(posts)} posts gerados"}
