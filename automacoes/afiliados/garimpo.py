"""
MÁQUINA 1: GARIMPO DE AFILIADOS
Busca produtos quentes na Hotmart, Kiwify e Eduzz, filtra por gravidade e te entrega
com link de afiliado + copy pronta + página de venda.
"""
import os
import json
import csv
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except:
    HAS_RICH = False

# Produtos simulados (na versão real, conecta na API da Hotmart/Kiwify)
PRODUTOS_EXEMPLO = [
    {"nome": "Método Renda em 7 Dias", "plataforma": "Kiwify", "preco": 97.00, "comissao": 70, "temperatura": 98, "categoria": "Renda Extra", "link": "https://kiwify.com.br/..."},
    {"nome": "Segredo do Milhão com PLR", "plataforma": "Hotmart", "preco": 197.00, "comissao": 80, "temperatura": 150, "categoria": "Marketing Digital", "link": "https://hotmart.com/..."},
    {"nome": "Pack Canva Lucrativo", "plataforma": "Eduzz", "preco": 47.00, "comissao": 60, "temperatura": 85, "categoria": "Design", "link": "https://eduzz.com/..."},
    {"nome": "Inglês em 30 Dias - Método Imersivo", "plataforma": "Hotmart", "preco": 297.00, "comissao": 65, "temperatura": 120, "categoria": "Educação", "link": "https://hotmart.com/..."},
    {"nome": "Receitas Seca Barriga", "plataforma": "Kiwify", "preco": 67.00, "comissao": 75, "temperatura": 110, "categoria": "Saúde", "link": "https://kiwify.com.br/..."},
]

def filtrar_quentes(produtos, min_temp=80, min_comissao=60):
    return [p for p in produtos if p["temperatura"] >= min_temp and p["comissao"] >= min_comissao]

def gerar_copy(produto):
    return f"""
🔥 {produto['nome']} - {produto['categoria']}

❌ Cansado de tentar e não ter resultado?
✅ Com o {produto['nome']} você aprende do ZERO e já vê resultado em poucos dias!

💰 Investimento: R$ {produto['preco']:.2f} (menos que uma pizza por mês)
🎁 Comissão para afiliado: {produto['comissao']}% = R$ {produto['preco']*produto['comissao']/100:.2f} por venda

👉 Garanta sua vaga agora: {produto['link']}?src=central

#rendaextra #marketingdigital #trabalheemcasa
""".strip()

def rodar_garimpo():
    if HAS_RICH:
        console.print("\n[bold cyan]🎯 MÁQUINA DE GARIMPO DE AFILIADOS[/bold cyan]")
        console.print("[dim]Buscando produtos com alta temperatura e comissão...[/dim]\n")
    else:
        print("\n🎯 GARIMPO DE AFILIADOS\n")

    quentes = filtrar_quentes(PRODUTOS_EXEMPLO)
    
    if HAS_RICH:
        table = Table(title=f"🔥 {len(quentes)} Produtos Quentes Encontrados", show_lines=True)
        table.add_column("Produto", style="bold")
        table.add_column("Plataforma", justify="center")
        table.add_column("Preço", justify="right", style="green")
        table.add_column("Comissão", justify="center", style="bold yellow")
        table.add_column("Temp.", justify="center", style="red")
        table.add_column("Ganho/Venda", justify="right", style="bold green")
        for p in quentes:
            ganho = p["preco"] * p["comissao"] / 100
            table.add_row(p["nome"], p["plataforma"], f"R$ {p['preco']:.2f}", f"{p['comissao']}%", str(p["temperatura"]), f"R$ {ganho:.2f}")
        console.print(table)

        # Salva CSV
        out = Path("exports")
        out.mkdir(exist_ok=True)
        csv_path = out / f"garimpo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=quentes[0].keys())
            w.writeheader()
            w.writerows(quentes)
        console.print(f"\n[green]✅ Salvo em {csv_path}[/green]")

        # Mostra copy do primeiro
        console.print("\n[bold]📋 COPY PRONTA (primeiro produto):[/bold]")
        console.print(Panel(gerar_copy(quentes[0]), title=quentes[0]["nome"], border_style="green"))

        console.print("\n[dim]Próximos passos:[/dim]")
        console.print("1. Peça afiliação nos 3 primeiros produtos")
        console.print("2. Use a copy acima no Instagram/WhatsApp")
        console.print("3. Rode [bold]python central.py --conteudo --tema \"{}\"[/bold] para gerar posts".format(quentes[0]['categoria']))
        input("\nPressione ENTER para voltar ao menu...")
    else:
        for p in quentes:
            print(f"- {p['nome']} | {p['plataforma']} | R$ {p['preco']} | {p['comissao']}% | Temp {p['temperatura']}")
        print("\nCopy do primeiro:\n", gerar_copy(quentes[0]))

if __name__ == "__main__":
    rodar_garimpo()
