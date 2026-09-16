"""
Dashboard simples com FastAPI - Mostra ganhos e controle central
Rode: python dashboard/app.py  -> http://localhost:8000
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from pathlib import Path
import json
import csv
from datetime import datetime

app = FastAPI(title="Central da Automação - Dashboard")

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Central da Automação - Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,sans-serif}
body{background:#0a0a0f;color:#e5e5e5;min-height:100vh}
header{background:linear-gradient(135deg,#00d084 0%,#00a86b 100%);padding:24px;text-align:center}
header h1{font-size:28px;font-weight:900;letter-spacing:-1px}
header p{opacity:.9;margin-top:6px}
.container{max-width:1100px;margin:24px auto;padding:0 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-bottom:24px}
.card{background:#1a1a24;border:1px solid #2a2a3a;border-radius:16px;padding:20px}
.card h3{font-size:13px;letter-spacing:1px;text-transform:uppercase;color:#9a9ab0;margin-bottom:8px}
.card .value{font-size:28px;font-weight:800}
.card .sub{font-size:13px;color:#7a7a9a;margin-top:4px}
.card.green{border-color:#00d08455;background:linear-gradient(135deg,#00d08415,#00d08405)}
.card.yellow{border-color:#f59e0b55;background:linear-gradient(135deg,#f59e0b15,#f59e0b05)}
.card.blue{border-color:#3b82f655;background:linear-gradient(135deg,#3b82f615,#3b82f605)}
.card.purple{border-color:#a855f755;background:linear-gradient(135deg,#a855f715,#a855f705)}
.panel{background:#1a1a24;border:1px solid #2a2a3a;border-radius:16px;padding:20px;margin-bottom:16px}
.panel h2{font-size:18px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.btn{display:inline-block;background:#00d084;color:#000;padding:10px 18px;border-radius:10px;font-weight:700;text-decoration:none;margin:4px 6px 4px 0;font-size:14px}
.btn.secondary{background:#2a2a3a;color:#fff}
table{width:100%;border-collapse:collapse}
th{color:#9a9ab0;font-size:12px;text-transform:uppercase;letter-spacing:1px;text-align:left;padding:10px;border-bottom:1px solid #2a2a3a}
td{padding:12px 10px;border-bottom:1px solid #1f1f2f;font-size:14px}
.badge{padding:4px 10px;border-radius:20px;font-size:12px;font-weight:700}
.badge.hot{background:#ef444415;color:#ef4444;border:1px solid #ef444435}
.badge.ok{background:#00d08415;color:#00d084;border:1px solid #00d08435}
.progress{height:8px;background:#2a2a3a;border-radius:20px;overflow:hidden;margin-top:8px}
.progress div{height:100%;background:linear-gradient(90deg,#00d084,#00a86b)}
footer{text-align:center;padding:24px;color:#5a5a7a;font-size:13px}
code{background:#2a2a3a;padding:2px 6px;border-radius:6px;font-size:13px}
</style>
</head>
<body>
<header>
<h1>💰 CENTRAL DA AUTOMAÇÃO</h1>
<p>Repositório Central de Criar Dinheiro • Salvador-BA • v1.0</p>
</header>
<div class="container">

<div class="grid">
<div class="card green"><h3>💵 Ganhos hoje (simulado)</h3><div class="value">R$ 247,80</div><div class="sub">+23% vs ontem • 4 vendas</div><div class="progress"><div style="width:73%"></div></div></div>
<div class="card yellow"><h3>🎯 Produtos garimpados</h3><div class="value">18</div><div class="sub">5 quentes com comissão >70%</div></div>
<div class="card blue"><h3>🤖 Posts gerados</h3><div class="value">42</div><div class="sub">12 agendados para hoje</div></div>
<div class="card purple"><h3>💬 Leads no bot</h3><div class="value">137</div><div class="sub">89 no Telegram • 48 WhatsApp</div></div>
</div>

<div class="panel">
<h2>⚡ Ações Rápidas</h2>
<a class="btn" href="#" onclick="alert('Rode no terminal: python central.py --menu')">🎮 Abrir Central (Terminal)</a>
<a class="btn secondary" href="#" onclick="alert('python central.py --afiliados')">🎯 Garimpar Produtos</a>
<a class="btn secondary" href="#" onclick="alert('python central.py --conteudo --tema renda extra --qtd 10')">🤖 Gerar Conteúdo</a>
<a class="btn secondary" href="#" onclick="alert('python central.py --bot telegram')">💬 Ativar Bot</a>
</div>

<div class="panel">
<h2>🔥 Top Produtos Quentes</h2>
<table>
<tr><th>Produto</th><th>Plataforma</th><th>Comissão</th><th>Status</th></tr>
<tr><td>Método Renda em 7 Dias</td><td>Kiwify</td><td>R$ 67,90 (70%)</td><td><span class="badge hot">🔥 Quente</span></td></tr>
<tr><td>Segredo do Milhão PLR</td><td>Hotmart</td><td>R$ 157,60 (80%)</td><td><span class="badge hot">🔥 Quente</span></td></tr>
<tr><td>Pack Canva Lucrativo</td><td>Eduzz</td><td>R$ 28,20 (60%)</td><td><span class="badge ok">✅ Ok</span></td></tr>
<tr><td>Receitas Seca Barriga</td><td>Kiwify</td><td>R$ 50,25 (75%)</td><td><span class="badge hot">🔥 Quente</span></td></tr>
</table>
</div>

<div class="panel">
<h2>📅 Posts Agendados (próximas 24h)</h2>
<table>
<tr><th>Horário</th><th>Título</th><th>Rede</th><th>Status</th></tr>
<tr><td>09:00</td><td>3 apps que me pagam todo dia...</td><td>Instagram • TikTok</td><td>⏰ Agendado</td></tr>
<tr><td>12:00</td><td>Como fiz meus primeiros R$100...</td><td>Instagram • Pinterest</td><td>⏰ Agendado</td></tr>
<tr><td>18:00</td><td>Erro que te impede de ganhar...</td><td>TikTok • YouTube Shorts</td><td>⏰ Agendado</td></tr>
</table>
</div>

<div class="panel">
<h2>🧠 Como usar</h2>
<p style="color:#9a9ab0;line-height:1.6">
1. Configure seu <code>.env</code> com as chaves (OpenAI, Telegram, etc)<br>
2. Rode <code>python central.py --menu</code> no terminal para controlar tudo<br>
3. Ou use <code>docker-compose up</code> para subir dashboard + n8n<br>
4. Veja tutoriais em <code>/docs</code> e workflows em <code>/n8n-workflows</code>
</p>
</div>

</div>
<footer>
Central da Automação • Feito em Salvador, Bahia 🇧🇷 • <a href="https://github.com/po0258611-maker/repositorio-cental-da-automa-o-de-criar-dinheiro" style="color:#00d084">GitHub</a><br>
Automatize o trabalho, escale os ganhos.
</footer>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/api/stats")
def stats():
    # Lê exports se existir
    stats = {"produtos": 0, "posts": 0, "ganhos_hoje": 247.80}
    try:
        if Path("exports").exists():
            stats["produtos"] = len(list(Path("exports").glob("*.csv")))
            stats["posts"] = len(list(Path("exports/conteudo").glob("*.json"))) if Path("exports/conteudo").exists() else 0
    except:
        pass
    return stats

if __name__ == "__main__":
    print("🚀 Dashboard em http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
