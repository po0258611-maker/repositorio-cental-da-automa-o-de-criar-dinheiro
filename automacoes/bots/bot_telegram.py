"""
MÁQUINA 4: BOT TELEGRAM / WHATSAPP
Vende 24h: responde dúvidas, envia link de afiliado, recupera carrinho.
Configure TELEGRAM_BOT_TOKEN no .env para rodar de verdade.
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except:
    HAS_RICH = False

MENSAGENS = {
    "/start": """👋 Olá! Eu sou o Bot da Central de Renda!

Escolha uma opção:
1️⃣ Quero começar do zero
2️⃣ Produtos mais vendidos hoje
3️⃣ Falar com humano

Digite o número 👇""",
    "1": """🚀 Para começar do zero:

✅ Passo 1: Escolha um produto quente (rode /produtos)
✅ Passo 2: Peça afiliação (aprovação em 24h)
✅ Passo 3: Use meus posts prontos para divulgar

Quer o guia gratuito? Digite GUIA""",
    "2": """🔥 TOP 3 PRODUTOS HOJE (comissão alta):

1. Método Renda 7 Dias - R$ 67,90/venda - /link1
2. Pack Canva Lucrativo - R$ 28,20/venda - /link2
3. Receitas Seca Barriga - R$ 50,25/venda - /link3

Digite o número do link que te envio na hora!""",
    "GUIA": """📘 Guia Gratuito enviado!

Acesse: https://seulink.com/guia

BÔNUS: 10 posts prontos para copiar e colar + grupo VIP no WhatsApp: https://wa.me/...

Dúvidas? Digite AJUDA"""
}

def simular_bot():
    if HAS_RICH:
        console.print(Panel(
            "🤖 MODO SIMULAÇÃO (sem token)\n\n"
            "Para ativar de verdade:\n"
            "1. Fale com @BotFather no Telegram\n"
            "2. Crie um bot e copie o TOKEN\n"
            "3. Cole no .env como TELEGRAM_BOT_TOKEN\n"
            "4. Rode novamente este módulo\n\n"
            "Enquanto isso, teste a conversa simulada abaixo:",
            title="BOT TELEGRAM", border_style="cyan"
        ))
        console.print("[bold green]Usuário:[/bold green] /start")
        console.print(f"[bold blue]Bot:[/bold blue] {MENSAGENS['/start']}\n")
        
        from rich.prompt import Prompt
        while True:
            msg = Prompt.ask("[bold green]Você[/bold green]", default="1")
            if msg.lower() in ["sair","exit","0"]:
                break
            resposta = MENSAGENS.get(msg.upper(), MENSAGENS.get(msg, "❓ Não entendi. Digite /start para ver o menu. Ou 'sair' para voltar."))
            console.print(f"[bold blue]Bot:[/bold blue] {resposta}\n")
            if msg.upper() == "GUIA":
                console.print("[dim]💰 O bot acabou de enviar seu link de afiliado e capturou o lead![/dim]\n")
    else:
        print("Modo simulação - Digite /start, 1, 2, GUIA ou sair")
        while True:
            m = input("Você: ")
            if m.lower() == "sair":
                break
            print("Bot:", MENSAGENS.get(m, MENSAGENS.get(m.upper(), "Não entendi")))

def rodar_bot(plataforma="telegram"):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if HAS_RICH:
        console.print(f"\n[bold cyan]💬 BOT {plataforma.upper()} - Vendedor 24h[/bold cyan]")
    
    if token and len(token) > 20 and ":" in token:
        # Tenta rodar bot real
        if HAS_RICH:
            console.print(f"[green]✅ Token encontrado! Iniciando bot {plataforma}...[/green]")
            console.print("[dim]Bot rodando... Envie /start no Telegram para testar. Ctrl+C para parar.[/dim]")
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
            
            async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text(MENSAGENS["/start"])
            
            async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
                texto = update.message.text.strip()
                resposta = MENSAGENS.get(texto, MENSAGENS.get(texto.upper(), "Digite /start para ver o menu 😊"))
                await update.message.reply_text(resposta)
            
            import asyncio
            async def main():
                app = Application.builder().token(token).build()
                app.add_handler(CommandHandler("start", start))
                app.add_handler(CommandHandler("produtos", lambda u,c: u.message.reply_text(MENSAGENS["2"])))
                app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
                print("Bot iniciado! Pressione Ctrl+C para parar.")
                await app.run_polling()
            
            # Se já estiver em loop, roda diferente
            import asyncio
            asyncio.run(main())
            
        except ImportError:
            if HAS_RICH:
                console.print("[yellow]⚠️ Instale: pip install python-telegram-bot[/yellow]")
            simular_bot()
        except Exception as e:
            if HAS_RICH:
                console.print(f"[red]Erro: {e}[/red]")
            simular_bot()
    else:
        simular_bot()
        if HAS_RICH:
            console.print("\n[dim]Dica: Configure o .env para ativar o bot real e vender no automático.[/dim]")
            input("Pressione ENTER para voltar...")

if __name__ == "__main__":
    rodar_bot()
