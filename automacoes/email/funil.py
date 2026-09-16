"""
MÁQUINA 6: E-MAIL MARKETING - FUNIL QUE VENDE DORMINDO
Cria sequência de 7 e-mails para cada produto afiliado.
Integrável com Brevo, Mailchimp ou Gmail (yagmail).
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except:
    HAS_RICH = False

SEQUENCIA = [
    {"dia": 0, "assunto": "🎁 Seu acesso liberado + bônus surpresa", "objetivo": "Entrega + Boas vindas", "cta": "Acessar material"},
    {"dia": 1, "assunto": "Você está cometendo esse erro? (90% erra)", "objetivo": "Gerar dor + autoridade", "cta": "Ver correção"},
    {"dia": 2, "assunto": "Case: Como a Ana fez R$ 1.237 em 7 dias", "objetivo": "Prova social", "cta": "Quero replicar"},
    {"dia": 3, "assunto": "Desconto de 50% expira hoje à meia-noite ⏰", "objetivo": "Escassez", "cta": "Garantir desconto"},
    {"dia": 5, "assunto": "Último aviso: vagas encerrando", "objetivo": "Última chamada", "cta": "Garantir vaga"},
    {"dia": 7, "assunto": "Você perdeu? Reabrimos por 24h", "objetivo": "Reabertura", "cta": "Entrar agora"},
]

def gerar_email(produto_nome, link, dia_info):
    return f"""Assunto: {dia_info['assunto']}

Olá {{nome}},

{dia_info['objetivo']} - sobre {produto_nome}

Hoje é o dia {dia_info['dia']} da sua jornada e preparei algo especial para você.

👉 {dia_info['cta']}: {link}

Qualquer dúvida, responda este e-mail.

Abraço,
Equipe Central da Automação

P.S. Link expira em 24h: {link}
"""

def rodar_email():
    if HAS_RICH:
        console.print("\n[bold cyan]📧 MÁQUINA DE E-MAIL - FUNIL AUTOMÁTICO[/bold cyan]")
        from rich.prompt import Prompt
        produto = Prompt.ask("📦 Nome do produto", default="Método Renda em 7 Dias")
        link = Prompt.ask("🔗 Seu link de afiliado", default="https://kiwify.com.br/seu-link")
    else:
        produto = input("Produto: ") or "Método Renda em 7 Dias"
        link = input("Link: ") or "https://kiwify.com.br/seu-link"

    if HAS_RICH:
        table = Table(title=f"📬 Sequência de 6 e-mails para: {produto}", show_lines=True)
        table.add_column("Dia", justify="center", style="cyan")
        table.add_column("Assunto", style="bold")
        table.add_column("Objetivo", style="dim")
        table.add_column("CTA", style="green")
        table.add_column("Data Envio", justify="center")
        
        inicio = datetime.now()
        for s in SEQUENCIA:
            data = inicio + timedelta(days=s["dia"])
            table.add_row(f"D+{s['dia']}", s["assunto"], s["objetivo"], s["cta"], data.strftime("%d/%m"))
        console.print(table)

        # Salva
        out = Path("exports/email")
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"funil_{produto.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(path, "w", encoding="utf-8") as f:
            for s in SEQUENCIA:
                f.write("="*60 + "\n")
                f.write(gerar_email(produto, link, s))
                f.write("\n\n")
        console.print(f"\n[green]✅ Funil salvo em {path}[/green]")
        
        console.print(Panel(
            "🚀 Como ativar envio automático:\n\n"
            "1. Gmail (grátis): Configure GMAIL_USER e GMAIL_APP_PASSWORD no .env\n"
            "   pip install yagmail -> yagmail.SMTP(...).send(...)\n\n"
            "2. Brevo (recomendado, 300/dia grátis):\n"
            "   Crie conta em brevo.com, pegue API KEY e cole no .env\n\n"
            "3. n8n: Importe n8n-workflows/email-funil.json e conecte sua lista\n\n"
            "💡 Leads: capture com o Bot Telegram + landing page",
            title="Próximos passos", border_style="yellow"
        ))
        input("\nPressione ENTER para voltar...")
    else:
        for s in SEQUENCIA:
            print(gerar_email(produto, link, s))

if __name__ == "__main__":
    rodar_email()
