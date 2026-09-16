#!/usr/bin/env python3
"""
REPOSITÓRIO CENTRAL DA AUTOMAÇÃO DE CRIAR DINHEIRO
Orquestrador Principal - Roda todas as automações de um só lugar
Autor: po0258611-maker | Salvador - BA
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

def banner():
    texto = r"""
 ██████╗███████╗███╗   ██╗████████╗██████╗  █████╗ ██╗     
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██╔══██╗██╔══██╗██║     
██║     █████╗  ██╔██╗ ██║   ██║   ██████╔╝███████║██║     
██║     ██╔══╝  ██║╚██╗██║   ██║   ██╔══██╗██╔══██║██║     
╚██████╗███████╗██║ ╚████║   ██║   ██║  ██║██║  ██║███████╗
 ╚═════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
 AUTOMAÇÃO DE CRIAR DINHEIRO  •  v1.0  •  Salvador-BA
    """
    if HAS_RICH:
        console.print(Panel(texto, style="bold green", box=box.DOUBLE, subtitle="💰 Automatize. Escale. Lucre."))
    else:
        print(texto)

def menu_principal():
    while True:
        banner()
        if HAS_RICH:
            table = Table(title="📋 MENU CENTRAL - Escolha sua máquina de dinheiro", box=box.ROUNDED, show_lines=True)
            table.add_column("#", style="cyan", justify="center")
            table.add_column("Máquina", style="bold white")
            table.add_column("O que faz", style="dim")
            table.add_column("Status", justify="center")
            
            table.add_row("1", "🎯 Garimpo Afiliados", "Hotmart/Kiwify/Eduzz - Produtos quentes + links", "✅ PRONTO")
            table.add_row("2", "🛒 Scraping Shopee/Amazon", "Acha produtos virais e monitora preços", "✅ PRONTO")
            table.add_row("3", "🤖 Fábrica de Conteúdo IA", "Gera posts, reels e scripts com IA", "✅ PRONTO")
            table.add_row("4", "💬 Bots WhatsApp/Telegram", "Vende e atende 24h no automático", "✅ PRONTO")
            table.add_row("5", "📱 Tráfego Automático", "Posta em Instagram/TikTok/Pinterest", "✅ PRONTO")
            table.add_row("6", "📧 E-mail Marketing", "Sequência que vende dormindo", "✅ PRONTO")
            table.add_row("7", "📊 Dashboard", "Ver ganhos e métricas", "🚧 EM BREVE")
            table.add_row("0", "🚪 Sair", "", "")
            console.print(table)
            console.print("[dim]Dica: Você pode rodar direto: python central.py --afiliados --conteudo --help[/dim]\n")
            escolha = Prompt.ask("👉 Digite o número da máquina", choices=["1","2","3","4","5","6","7","0"], default="1")
        else:
            print("\n1 - Garimpo Afiliados\n2 - Scraping\n3 - Conteúdo IA\n4 - Bots\n5 - Tráfego\n6 - Email\n7 - Dashboard\n0 - Sair")
            escolha = input("Escolha: ").strip()

        if escolha == "1":
            from automacoes.afiliados.garimpo import rodar_garimpo
            rodar_garimpo()
        elif escolha == "2":
            from automacoes.scraping.monitor import rodar_scraping
            rodar_scraping()
        elif escolha == "3":
            from automacoes.conteudo_ia.gerador import rodar_gerador
            rodar_gerador()
        elif escolha == "4":
            from automacoes.bots.bot_telegram import rodar_bot
            rodar_bot()
        elif escolha == "5":
            from automacoes.trafego.autopost import rodar_trafego
            rodar_trafego()
        elif escolha == "6":
            from automacoes.email.funil import rodar_email
            rodar_email()
        elif escolha == "7":
            if HAS_RICH:
                console.print(Panel("📊 Dashboard Web em desenvolvimento!\nRode: [bold]python dashboard/app.py[/bold]\nDepois acesse http://localhost:8000", style="yellow"))
            else:
                print("Dashboard em breve - python dashboard/app.py")
            input("Pressione ENTER para voltar...")
        elif escolha == "0":
            if HAS_RICH:
                console.print("[bold green]👋 Até a próxima! Bora automatizar e lucrar![/bold green]")
            else:
                print("Até a próxima!")
            sys.exit(0)

def modo_cli():
    import argparse
    parser = argparse.ArgumentParser(description="Central da Automação de Criar Dinheiro")
    parser.add_argument("--menu", action="store_true", help="Abre menu interativo")
    parser.add_argument("--afiliados", action="store_true", help="Roda garimpo de afiliados")
    parser.add_argument("--scraping", action="store_true", help="Roda scraping Shopee/Amazon")
    parser.add_argument("--conteudo", action="store_true", help="Gera conteúdo com IA")
    parser.add_argument("--tema", type=str, default="renda extra", help="Tema para conteúdo")
    parser.add_argument("--qtd", type=int, default=5, help="Quantidade de posts")
    parser.add_argument("--bot", type=str, choices=["telegram","whatsapp"], help="Inicia bot")
    parser.add_argument("--trafego", action="store_true", help="Roda tráfego automático")
    parser.add_argument("--dashboard", action="store_true", help="Inicia dashboard")
    args = parser.parse_args()

    if len(sys.argv) == 1 or args.menu:
        menu_principal()
    elif args.afiliados:
        from automacoes.afiliados.garimpo import rodar_garimpo
        rodar_garimpo()
    elif args.scraping:
        from automacoes.scraping.monitor import rodar_scraping
        rodar_scraping()
    elif args.conteudo:
        from automacoes.conteudo_ia.gerador import rodar_gerador
        rodar_gerador(tema=args.tema, qtd=args.qtd)
    elif args.bot:
        from automacoes.bots.bot_telegram import rodar_bot
        rodar_bot(plataforma=args.bot)
    elif args.trafego:
        from automacoes.trafego.autopost import rodar_trafego
        rodar_trafego()
    elif args.dashboard:
        os.system("python dashboard/app.py")
    else:
        menu_principal()

if __name__ == "__main__":
    modo_cli()
