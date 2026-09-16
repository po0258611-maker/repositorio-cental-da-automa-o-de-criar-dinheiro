"""
MÁQUINA 2: SCRAPING SHOPEE / AMAZON / ALIEXPRESS
Monitora preços, encontra produtos virais e gera lista para afiliado ou dropshipping.
Na versão real usa Playwright/Selenium + API Shopee.
Aqui versão demo com dados simulados.
"""
import csv
import random
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except:
    HAS_RICH = False

PRODUTOS_VIRAIS = [
    {"produto": "Mini Projetor 4K Portátil", "preco_atual": 299.90, "preco_antes": 599.90, "vendas_mes": 3420, "avaliacao": 4.8, "loja": "Shopee", "comissao": 12, "link": "https://shopee.com.br/..."},
    {"produto": "Fone Bluetooth P9 Sem Fio", "preco_atual": 59.90, "preco_antes": 129.90, "vendas_mes": 8900, "avaliacao": 4.7, "loja": "Shopee", "comissao": 10, "link": "https://shopee.com.br/..."},
    {"produto": "Escova Secadora 5 em 1", "preco_atual": 89.90, "preco_antes": 199.90, "vendas_mes": 5600, "avaliacao": 4.9, "loja": "Amazon", "comissao": 8, "link": "https://amazon.com.br/..."},
    {"produto": "Câmera WiFi 360º", "preco_atual": 79.90, "preco_antes": 149.90, "vendas_mes": 2100, "avaliacao": 4.6, "loja": "Shopee", "comissao": 15, "link": "https://shopee.com.br/..."},
    {"produto": "Relógio Smartwatch T900", "preco_atual": 119.90, "preco_antes": 249.90, "vendas_mes": 4300, "avaliacao": 4.7, "loja": "AliExpress", "comissao": 9, "link": "https://aliexpress.com/..."},
]

def calcular_oportunidade(p):
    desconto = (1 - p["preco_atual"]/p["preco_antes"])*100
    score = (p["vendas_mes"]/100) + (p["avaliacao"]*10) + desconto
    return round(score,1), round(desconto,1)

def rodar_scraping():
    if HAS_RICH:
        console.print("\n[bold cyan]🛒 MONITOR DE PRODUTOS VIRAIS[/bold cyan]")
        console.print("[dim]Varrendo Shopee, Amazon e AliExpress... (modo demo)[/dim]\n")
    else:
        print("\n🛒 SCRAPING PRODUTOS VIRAIS\n")

    lista = []
    for p in PRODUTOS_VIRAIS:
        score, desconto = calcular_oportunidade(p)
        p2 = {**p, "desconto": desconto, "score": score, "lucro_venda": round(p["preco_atual"]*p["comissao"]/100,2)}
        lista.append(p2)
    
    lista.sort(key=lambda x: x["score"], reverse=True)

    if HAS_RICH:
        table = Table(title="🔥 Ranking de Oportunidades (Maior Score = Mais Viral)", show_lines=True)
        table.add_column("Produto", style="bold")
        table.add_column("Loja", justify="center")
        table.add_column("Preço", justify="right", style="green")
        table.add_column("Desconto", justify="center", style="red")
        table.add_column("Vendas/mês", justify="center")
        table.add_column("⭐", justify="center")
        table.add_column("Comissão", justify="center", style="yellow")
        table.add_column("Score", justify="center", style="bold cyan")
        for p in lista:
            table.add_row(p["produto"], p["loja"], f"R$ {p['preco_atual']:.2f}", f"{p['desconto']:.0f}%", str(p["vendas_mes"]), str(p["avaliacao"]), f"R$ {p['lucro_venda']:.2f}", str(p["score"]))
        console.print(table)

        out = Path("exports")
        out.mkdir(exist_ok=True)
        csv_path = out / f"virais_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            import csv
            w = csv.DictWriter(f, fieldnames=lista[0].keys())
            w.writeheader()
            w.writerows(lista)
        console.print(f"\n[green]✅ Lista salva em {csv_path}[/green]")
        console.print(Panel(
            f"🎬 Ideia de vídeo viral para o TOP 1:\n\n"
            f"\"{lista[0]['produto']} por APENAS R$ {lista[0]['preco_atual']:.2f} 😱 "
            f"De R$ {lista[0]['preco_antes']:.2f} por {lista[0]['desconto']:.0f}% OFF! Link no primeiro comentário 👇\"\n\n"
            f"Comissão: R$ {lista[0]['lucro_venda']:.2f} por venda. 10 vendas/dia = R$ {lista[0]['lucro_venda']*10:.2f}/dia",
            title="💡 O QUE FAZER AGORA", border_style="yellow"
        ))
        input("\nPressione ENTER para voltar...")
    else:
        for p in lista:
            print(p)

if __name__ == "__main__":
    rodar_scraping()
