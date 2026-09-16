"""
MÁQUINA 3: FÁBRICA DE CONTEÚDO COM IA
Gera posts, carrosséis, scripts de Reels/TikTok e descrições usando OpenAI/Gemini.
Se não tiver API key, usa modo template (funciona offline).
"""
import os
import json
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except:
    HAS_RICH = False

TEMPLATES = {
    "renda extra": [
        "3 apps que me pagam todo dia (o 3º é o melhor) 💰",
        "Como fiz meus primeiros R$ 100 no celular sem aparecer",
        "Erro que te impede de ganhar dinheiro online (e como corrigir)",
        "Renda extra que ninguém te conta em 2024",
    ],
    "marketing digital": [
        "Como vender todo dia sem precisar aparecer",
        "Funil que vende enquanto você dorme",
        "O segredo dos afiliados que faturam 6 dígitos",
    ],
    "saúde": [
        "3 hábitos que mudaram minha energia em 7 dias",
        "Receita seca barriga que viralizou",
    ]
}

HASHTAGS = {
    "renda extra": "#rendaextra #dinheiroonline #trabalheemcasa #rendaextraemcasa #marketingdigital",
    "marketing digital": "#marketingdigital #afiliados #hotmart #kiwify #vendas",
    "saúde": "#saude #emagrecimento #receitafit #vidasaudavel"
}

def gerar_com_ia(tema, qtd):
    """Tenta usar OpenAI, se não tiver usa template"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-") and len(api_key) > 20:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prompt = f"Crie {qtd} ideias de posts virais para Instagram Reels sobre '{tema}'. Para cada: título chamativo, roteiro de 30s, legenda com CTA e hashtags. Retorne em JSON lista com keys: titulo, roteiro, legenda, hashtags"
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content": prompt}],
                temperature=0.9
            )
            texto = resp.choices[0].message.content
            # tenta extrair JSON
            try:
                # procura [...] no texto
                import re
                m = re.search(r'\[.*\]', texto, re.DOTALL)
                if m:
                    return json.loads(m.group(0))
            except:
                pass
            # fallback: retorna texto cru dividido
            return [{"titulo": f"Ideia {i+1}", "roteiro": texto[:500], "legenda": texto[:300], "hashtags": HASHTAGS.get(tema, "#viral")} for i in range(qtd)]
        except Exception as e:
            print(f"⚠️ Erro IA ({e}), usando modo template...")
    
    # MODO TEMPLATE (offline)
    base = TEMPLATES.get(tema.lower(), TEMPLATES["renda extra"])
    hashtags = HASHTAGS.get(tema.lower(), "#viral #rendaextra #marketingdigital")
    posts = []
    for i in range(qtd):
        titulo = random.choice(base) + f" #{i+1}"
        roteiro = f"""[0-3s] Gancho: "{titulo}" (texto grande na tela + música viral)
[3-15s] Entrega 3 dicas rápidas sobre {tema} (corte dinâmico, legenda automática)
[15-28s] Prova: print de resultado / antes e depois
[28-30s] CTA: "Comenta EU QUERO que te mando o link no direct 👇" """
        legenda = f"""{titulo} 🔥

Você sabia que dá para começar no {tema} com 0 seguidores?

✅ Sem precisar aparecer
✅ Só com celular
✅ Passo a passo no link da bio

Comenta "EU QUERO" que te envio o guia gratuito 👇

{hashtags}"""
        posts.append({"titulo": titulo, "roteiro": roteiro, "legenda": legenda, "hashtags": hashtags})
    return posts

def rodar_gerador(tema=None, qtd=None):
    if tema is None:
        if HAS_RICH:
            console.print("\n[bold cyan]🤖 FÁBRICA DE CONTEÚDO COM IA[/bold cyan]")
            from rich.prompt import Prompt, IntPrompt
            tema = Prompt.ask("📌 Qual o tema?", default="renda extra")
            qtd = IntPrompt.ask("🔢 Quantos posts?", default=5)
        else:
            tema = input("Tema (renda extra): ") or "renda extra"
            qtd = int(input("Qtd (5): ") or 5)
    else:
        qtd = qtd or 5

    if HAS_RICH:
        console.print(f"\n[dim]Gerando {qtd} posts sobre '{tema}'...[/dim]")

    posts = gerar_com_ia(tema, qtd)

    out = Path("exports/conteudo")
    out.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    json_path = out / f"posts_{tema.replace(' ','_')}_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    if HAS_RICH:
        for i, p in enumerate(posts, 1):
            console.print(Panel(
                f"[bold]{p['titulo']}[/bold]\n\n"
                f"[cyan]🎬 ROTEIRO:[/cyan]\n{p['roteiro']}\n\n"
                f"[green]📝 LEGENDA:[/green]\n{p['legenda']}",
                title=f"POST {i}/{qtd}", border_style="blue"
            ))
        console.print(f"\n[green]✅ {qtd} posts salvos em {json_path}[/green]")
        console.print("[dim]Próximo: python central.py --trafego  para postar automaticamente[/dim]")
        if tema is None or qtd is None:
            input("\nPressione ENTER para voltar...")
    else:
        for p in posts:
            print(f"\n--- {p['titulo']} ---\n{p['legenda']}\n")
        print(f"Salvo em {json_path}")

if __name__ == "__main__":
    rodar_gerador()
