"""
MÁQUINA 5: TRÁFEGO AUTOMÁTICO
Lê posts gerados em exports/conteudo/ e agenda autopost para Instagram, TikTok, Pinterest, X.
Versão demo: simula agendamento. Versão real usa instagrapi / APIs.
"""
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except:
    HAS_RICH = False

REDES = ["Instagram", "TikTok", "Pinterest", "X (Twitter)", "YouTube Shorts"]

def rodar_trafego():
    pasta = Path("exports/conteudo")
    arquivos = list(pasta.glob("*.json")) if pasta.exists() else []
    
    if HAS_RICH:
        console.print("\n[bold cyan]📱 MÁQUINA DE TRÁFEGO AUTOMÁTICO[/bold cyan]")
    
    if not arquivos:
        if HAS_RICH:
            console.print(Panel(
                "⚠️ Nenhum conteúdo encontrado!\n\n"
                "Primeiro gere posts:\n"
                "[bold]python central.py --conteudo --tema \"renda extra\" --qtd 10[/bold]\n\n"
                "Depois volte aqui para agendar os posts.",
                title="Aviso", border_style="yellow"
            ))
            from rich.prompt import Prompt
            if Prompt.ask("Gerar 5 posts de demonstração agora?", choices=["s","n"], default="s") == "s":
                from automacoes.conteudo_ia.gerador import gerar_com_ia
                import json as js
                posts = gerar_com_ia("renda extra", 5)
                pasta.mkdir(parents=True, exist_ok=True)
                p = pasta / f"posts_renda_extra_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
                with open(p, "w", encoding="utf-8") as f:
                    js.dump(posts, f, ensure_ascii=False, indent=2)
                console.print(f"[green]✅ 5 posts gerados em {p}[/green]")
                arquivos = [p]
            else:
                input("Pressione ENTER para voltar...")
                return
        else:
            print("Nenhum conteúdo. Rode o gerador primeiro.")
            return
        arquivos = list(pasta.glob("*.json"))

    # Pega arquivo mais recente
    arquivo = max(arquivos, key=lambda p: p.stat().st_mtime)
    with open(arquivo, encoding="utf-8") as f:
        posts = json.load(f)

    if HAS_RICH:
        console.print(f"[dim]Encontrado: {arquivo.name} com {len(posts)} posts[/dim]\n")
        
        # Simula agendamento
        table = Table(title="📅 Agendamento Simulado (1 post a cada 3 horas)", show_lines=True)
        table.add_column("#", justify="center")
        table.add_column("Título", style="bold")
        table.add_column("Rede", justify="center")
        table.add_column("Data/Hora", justify="center", style="cyan")
        table.add_column("Status", justify="center")
        
        inicio = datetime.now() + timedelta(minutes=10)
        for i, p in enumerate(posts[:5]):
            for rede in random.sample(REDES, 2):  # 2 redes por post
                dt = inicio + timedelta(hours=i*3)
                table.add_row(str(i+1), p["titulo"][:40]+"...", rede, dt.strftime("%d/%m %H:%M"), "⏰ Agendado")
        
        console.print(table)
        
        console.print(Panel(
            "✅ [bold green]MODO SIMULAÇÃO ATIVO[/bold green]\n\n"
            "Para postar DE VERDADE:\n"
            "1. Configure INSTAGRAM_USERNAME e PASSWORD no .env\n"
            "2. Instale: pip install instagrapi\n"
            "3. Descomente o código real em automacoes/trafego/autopost.py\n\n"
            "💡 Dica PRO: Use n8n (docker-compose up) para postar sem tomar block.",
            title="Como ativar postagem real", border_style="green"
        ))
        
        # Código real comentado de exemplo
        console.print("\n[dim]Exemplo de código real (descomente para usar):[/dim]")
        console.print("[dim]---\nfrom instagrapi import Client\ncl = Client()\ncl.login(os.getenv('INSTAGRAM_USERNAME'), os.getenv('INSTAGRAM_PASSWORD'))\ncl.photo_upload(path, caption=post['legenda'])\n---[/dim]")
        
        input("\nPressione ENTER para voltar...")
    else:
        print(f"Agendando {len(posts)} posts...")

# Código real pronto (descomente quando configurar)
"""
import os
from instagrapi import Client

def postar_instagram(post, imagem_path):
    cl = Client()
    cl.login(os.getenv("INSTAGRAM_USERNAME"), os.getenv("INSTAGRAM_PASSWORD"))
    cl.photo_upload(imagem_path, caption=post["legenda"])
    print("✅ Postado no Instagram!")
"""

if __name__ == "__main__":
    rodar_trafego()
