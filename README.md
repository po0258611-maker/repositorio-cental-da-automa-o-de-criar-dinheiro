# 💰 AUTONOMOUS MONEY ENGINE — AME

> **Plataforma de automação empresarial orientada à geração de receita. Loop autônomo que pensa, planeja, constrói, vende, mede, aprende e reinveste.**

[![AME Version](https://img.shields.io/badge/AME-v1.0.0-00d084?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)]()
[![License](https://img.shields.io/badge/Licença-MIT-green?style=flat-square)]()
[![Agents](https://img.shields.io/badge/Agentes-27-8a2be2?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Produção-success?style=flat-square)]()

**Repositório:** `po0258611-maker/repositorio-cental-da-automa-o-de-criar-dinheiro`  
**Branch principal:** `main`  
**Ambiente:** Salvador, Bahia 🇧🇷 — `America/Sao_Paulo`

---

## 🎯 Objetivo

Construir um **sistema econômico autônomo** capaz de operar sem intervenção humana contínua:

**OBSERVE → RESEARCH → DISCOVER → VALIDATE → DECIDE → BUILD → PUBLISH → DISTRIBUTE → SELL → MEASURE → LEARN → OPTIMIZE → REINVEST → REPEAT**

O AME descobre oportunidades, valida com evidência, cria produtos digitais automaticamente (ebooks, PDFs, imagens, copies, vídeos, landing pages), distribui em múltiplos canais (SEO, social, email, ads), vende, mede CAC/LTV/ROI/ROAS, aprende com sucessos e falhas, e reinveste — preservando caixa em modo SURVIVAL/EMERGENCY.

**Não é um consultor. É o AGENTE EXECUTOR.**

---

## 🏗️ Arquitetura

```
AME/
├── app/
│   ├── core/               # Núcleo
│   │   ├── config.py       # Pydantic Settings + .env
│   │   ├── database.py     # SQLAlchemy 2.0 (sync+async) + Base
│   │   ├── security.py     # JWT, hash, rate-limit, sanitize
│   │   ├── observability.py# logs estruturados + Prometheus
│   │   ├── events.py       # EventBus (15 eventos)
│   │   ├── tools.py        # ToolSystem (name/cost/risk/timeout/retry)
│   │   ├── llm_router.py   # LLM_PROVIDER (OpenAI, Anthropic, Gemini, Groq)
│   │   ├── economic.py     # EconomicEngine (PROFIT, MARGIN, ROI, RUNWAY, MODE)
│   │   ├── experiment.py   # ExperimentEngine (IDEA→ARCHIVED)
│   │   ├── memory.py       # MemoryStore (9 categorias)
│   │   └── orchestrator.py # Orchestrator (cérebro + loop 14 fases)
│   ├── models/
│   │   └── base.py         # 18 entidades (users, agents, tasks, projects, ...)
│   ├── agents/             # 27 agentes especializados
│   │   ├── base.py
│   │   ├── orchestrator_agent.py
│   │   ├── research_agents.py   (MARKET, TREND, COMPETITOR, VALIDATION)
│   │   ├── product_agents.py    (STRATEGIST, BUILDER, DIGITAL_PRODUCT, LANDING_PAGE)
│   │   ├── creative_agents.py   (COPY, IMAGE, VIDEO, CONTENT)
│   │   ├── growth_agents.py     (SEO, SOCIAL, ADS, SALES, EMAIL)
│   │   ├── finance_agents.py    (CFO, ECONOMIC, PRICING)
│   │   ├── quality_agents.py    (QA, SECURITY, RISK)
│   │   └── learning_agents.py   (ANALYTICS, EXPERIMENT, LEARNING)
│   ├── providers/
│   │   ├── image_provider.py    # IMAGE_PROVIDER (Replicate/Stability/OpenAI/mock)
│   │   ├── video_provider.py    # VIDEO_PROVIDER
│   │   ├── document_provider.py # DOCUMENT_PROVIDER (ebook/pdf/template)
│   │   └── browser_provider.py  # Browser automation (Playwright/BS4)
│   ├── services/
│   │   ├── discovery.py    # Pesquisa mercado + tendências
│   │   ├── validation.py   # Validação demanda/preço/monetização
│   │   ├── creation.py     # Criação automática de produtos
│   │   ├── distribution.py # Distribuição multi-canal
│   │   ├── sales.py        # Funil + checkout
│   │   └── intelligence.py # CFO + métricas
│   ├── api/                # 13 grupos de endpoints
│   │   ├── health.py       # /health, /ready, /live
│   │   ├── agents.py       # /agents
│   │   ├── tasks.py        # /tasks
│   │   ├── experiments.py  # /experiments
│   │   ├── products.py     # /products (+discover/validate/create-bundle)
│   │   ├── marketing.py    # /marketing
│   │   ├── sales.py        # /sales (+leads)
│   │   ├── finance.py      # /finance
│   │   ├── analytics.py    # /analytics
│   │   ├── memory.py       # /memory
│   │   ├── integrations.py # /integrations + /tools
│   │   └── system.py       # /system
│   └── main.py             # FastAPI app (lifespan, CORS, middleware)
├── automacoes/             # Legado (6 máquinas) - reaproveitado como tools
│   ├── afiliados/          # Hotmart/Kiwify/Eduzz
│   ├── scraping/           # Shopee/Amazon
│   ├── conteudo_ia/        # Geração com IA
│   ├── bots/               # Telegram/WhatsApp
│   ├── trafego/            # Autopost
│   └── email/              # Funil
├── dashboard/
│   ├── index.html          # Dashboard AME (Financeiro, Produtos, Experimentos, Marketing, Sistema)
│   └── app.py              # Legacy dashboard (compat)
├── scripts/
│   ├── init_db.py          # Cria tabelas + seed agents/integrations
│   └── seed.py             # Seed demo (produtos, leads, experiments, economic)
├── tests/
│   ├── test_economic.py
│   ├── test_experiment.py
│   ├── test_api.py
│   └── test_agents.py
├── docs/
│   ├── GUIA_RAPIDO.md
│   └── ESTRATEGIA.md
├── central.py              # Orquestrador legado (menu CLI)
├── .env.example            # Variáveis documentadas
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Multi-Agent System (27 agentes)

| Camada | Agentes |
|--------|---------|
| **CORE** | `ORCHESTRATOR_AGENT` |
| **RESEARCH** | `MARKET_AGENT`, `TREND_AGENT`, `COMPETITOR_AGENT`, `VALIDATION_AGENT` |
| **PRODUCT** | `PRODUCT_STRATEGIST_AGENT`, `PRODUCT_BUILDER_AGENT`, `DIGITAL_PRODUCT_AGENT`, `LANDING_PAGE_AGENT` |
| **CREATIVE** | `COPY_AGENT`, `IMAGE_AGENT`, `VIDEO_AGENT`, `CONTENT_AGENT` |
| **GROWTH** | `SEO_AGENT`, `SOCIAL_AGENT`, `ADS_AGENT`, `SALES_AGENT`, `EMAIL_AGENT` |
| **FINANCE** | `CFO_AGENT`, `ECONOMIC_AGENT`, `PRICING_AGENT` |
| **QUALITY** | `QA_AGENT`, `SECURITY_AGENT`, `RISK_AGENT` |
| **LEARNING** | `ANALYTICS_AGENT`, `EXPERIMENT_AGENT`, `LEARNING_AGENT` |

O **ORCHESTRATOR** avalia `economic.mode`, `experiments`, `memory`, `falhas`, `custo` e seleciona **apenas os agentes necessários** (ex: nova oportunidade → MARKET→VALIDATION→PRODUCT→COPY→LANDING; CAC alto → ANALYTICS→CFO→EXPERIMENT).

---

## 🚀 Instalação

### 1. Clone
```bash
git clone https://github.com/po0258611-maker/repositorio-cental-da-automa-o-de-criar-dinheiro.git
cd repositorio-cental-da-automa-o-de-criar-dinheiro
```

### 2. Ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Configuração
```bash
cp .env.example .env
# Edite .env com suas chaves (OPENAI_API_KEY, TELEGRAM_BOT_TOKEN, etc)
# O sistema funciona em MOCK sem chaves (modo demo)
```

### 4. Banco + Seed
```bash
python scripts/init_db.py
python scripts/seed.py
```

### 5. Rodar
```bash
# API + Dashboard AME (recomendado)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Acesse:
# Dashboard: http://localhost:8000/  ou  http://localhost:8000/dashboard
# Docs:      http://localhost:8000/docs
# Health:    http://localhost:8000/health

# OU legado:
python central.py --menu
# OU docker:
docker-compose up --build
# Ame: http://localhost:8000 | n8n: http://localhost:5678 (admin/central123)
```

---

## ⚙️ Configuração (.env)

Todas as variáveis estão documentadas em `.env.example`. Obrigatórias mínimas: nenhuma (roda em mock). Para produção:

```env
AME_ENV=production
DATABASE_URL=sqlite:///./ame.db  # ou postgresql+asyncpg://user:pass@db:5432/ame
AME_SECRET_KEY=sua-chave-32-chars-secreta
JWT_SECRET=seu-jwt-secret-32-chars

OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=...
TELEGRAM_BOT_TOKEN=123456:ABC...

AME_INITIAL_BALANCE=1000.00
AME_MAX_DAILY_AI_COST_USD=10.00
```

**Nunca commit `.env` com secrets.** O `.gitignore` já protege.

---

## ▶️ Execução

### Loop Autônomo (Orchestrator)
```bash
curl -X POST http://localhost:8000/agents/orchestrator/cycle
# ou
curl -X POST http://localhost:8000/system/loop/start
```
O Orchestrator avança `OBSERVE→...→REPEAT`, avalia `PRIORIDADE #39` (falhas críticas > estabilidade > segurança > receita > validação > conversão > custo > expansão) e dispara agentes.

### Pipeline Completo (Discovery → Venda)
```bash
# 1. Descobrir
curl -X POST http://localhost:8000/products/discover -H "Content-Type: application/json" -d '{"niche_hint":"renda extra"}'

# 2. Validar
curl -X POST http://localhost:8000/products/validate -H "Content-Type: application/json" -d '{"nicho":"IA para PMEs","score":92}'

# 3. Criar bundle (ebook+landing+copy+imagem)
curl -X POST http://localhost:8000/products/create-bundle -H "Content-Type: application/json" -d '{"go":true,"mvp":"Ebook + templates"}'

# 4. Distribuir
curl -X POST http://localhost:8000/marketing/distribute -H "Content-Type: application/json" -d '{"product_bundle":{"product":"Ebook IA"},"channels":["social","seo","email"]}'

# 5. Vender
curl -X POST http://localhost:8000/sales/sales -H "Content-Type: application/json" -d '{"amount":97,"customer_email":"cliente@teste.com"}'

# 6. Ver inteligência
curl http://localhost:8000/analytics/dashboard
```

### CLI Legado
```bash
python central.py --menu              # Menu 6 máquinas
python central.py --afiliados         # Garimpo Hotmart/Kiwify
python central.py --conteudo --tema "renda extra" --qtd 5
python central.py --scraping
python central.py --bot telegram
```

---

## 🔐 Ambiente & Variáveis

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `AME_ENV` | não | `development` | `development`/`production` |
| `DATABASE_URL` | não | `sqlite:///./ame.db` | Conexão DB |
| `AME_SECRET_KEY` | sim prod | `change-me` | Chave app |
| `JWT_SECRET` | sim prod | `change-me` | Assinatura JWT |
| `OPENAI_API_KEY` | não | — | LLM (fallback mock) |
| `GEMINI_API_KEY` | não | — | LLM fallback |
| `TELEGRAM_BOT_TOKEN` | não | — | Bot vendas |
| `AME_MAX_DAILY_AI_COST_USD` | não | `10.00` | Teto IA/dia |
| `AME_INITIAL_BALANCE` | não | `1000` | Saldo inicial |

Veja lista completa em `.env.example` (50+ vars).

---

## 🧪 Desenvolvimento

```bash
# Formato
# app/core/*  → núcleo (economic, experiment, orchestrator, etc)
# app/agents/*→ 27 agentes (herdam BaseAgent)
# app/providers/* → IMAGE/VIDEO/DOCUMENT/BROWSER
# app/services/* → discovery, validation, creation, distribution, sales, intelligence

# Adicionar novo agente:
# 1. Crie app/agents/meu_agente.py herding BaseAgent
# 2. Registre em app/agents/__init__.py AGENTS dict
# 3. O Orchestrator já selecionará automaticamente

# Adicionar tool:
from app.core.tools import tool, ToolRisk
@tool(name="minha_tool", description="...", cost=0.01, risk=ToolRisk.LOW)
def minha_tool(arg: str) -> dict:
    return {"ok": True}
```

---

## ✅ Testes

```bash
pytest -v
# ou
python tests/test_economic.py
python tests/test_experiment.py
python tests/test_api.py      # TestClient FastAPI (health, agents, experiments, finance, products, memory, orchestrator)
python tests/test_agents.py   # Roda 27 agentes + 1 ciclo orchestrator

# Cobertura
pytest --cov=app tests/
```

**Critério do prompt #27:** nenhum deploy sem testes. Se falhar → corrigir → testar novamente.

---

## 🐳 Deploy

### Docker (recomendado)
```bash
docker-compose up --build -d
# Verifica:
curl http://localhost:8000/health
docker logs ame-core -f
```

### Manual + Smoke Test
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 &
sleep 3
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:8000/agents | grep orchestrator_agent || exit 1
echo "✅ Smoke test passed"
```

### GitHub Workflow
```
ANALYZE → CREATE BRANCH → IMPLEMENT → TEST → FIX → COMMIT → PUSH → CI → VERIFY → MERGE/PR
```
Commits semânticos: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`, `perf:`, `security:`.

---

## 📊 Dashboard

`http://localhost:8000/` — `dashboard/index.html`

- **Financeiro:** Saldo, Receita, Despesa, Lucro, Margem, ROI, Runway, Modo (GROW/NORMAL/SURVIVAL/EMERGENCY), Burn, Custo IA
- **Produtos:** Ativos, vencedores, em teste, arquivados (+ criar via UI)
- **Experimentos:** Ativos, validação, vencedores, falhas (tabela + criar/avaliar)
- **Marketing:** Impressões, Cliques, CTR, Leads, CAC, Conversão, ROAS
- **Sistema:** Agentes ativos (27), Tasks, Erros, Custos IA, APIs, Latência, Health, Memória, Eventos

Polling a cada 10s em `/finance/dashboard`, `/experiments`, `/analytics/*`.

---

## 🔍 Observability

- **Logs estruturados:** `structlog` JSON (ou console em DEBUG)
- **Métricas:** `prometheus_client` (`ame_requests_total`, `ame_revenue_total`, `ame_ai_cost_usd`, etc) + `metrics_store` em memória para dashboard
- **Health:** `GET /health` → `{status, services:{database, ai_router, orchestrator, event_bus}, uptime}`
- **Events:** `GET /analytics/events?limit=20` (histórico EventBus)
- **Tracing:** `X-AME-Latency` header por request

---

## 🔒 Segurança

- `sanitize_input()` bloqueia `<script`, `javascript:` etc
- `rate_limit()` por IP (in-memory; em prod use Redis)
- `hash_password` / `verify_password` (bcrypt + passlib)
- `create_access_token` / `decode_token` (JWT HS256)
- Secrets **nunca** no código; só via `.env` + `mask_secret()` em logs
- `.gitignore` protege `.env`, `ame.db`, `ame_memory.json`

---

## 🧠 Memória & Aprendizado

9 categorias persistidas em `ame_memory.json` (e tabela `memory`):

`market_memory`, `product_memory`, `customer_memory`, `marketing_memory`, `financial_memory`, `experiment_memory`, `failure_memory`, `success_memory`, `system_memory`

Cada execução registra `ACTION, RESULT, COST, METRIC, LESSON, NEXT_ACTION`. O `LEARNING_AGENT` evita repetir estratégia fracassada sem nova hipótese (`should_avoid()`).

---

## 🛠️ Troubleshooting

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError: pydantic_settings` | `pip install pydantic-settings` ou `pip install -r requirements.txt` |
| `address already in use :8000` | `lsof -i :8000` ou troque porta: `uvicorn app.main:app --port 8001` |
| `No API key for LLMProvider` | Normal em mock; configure `OPENAI_API_KEY` para real. Custo limitado por `AME_MAX_DAILY_AI_COST_USD` |
| `metadata is reserved` (SQLAlchemy) | Já corrigido: attr `extra_data` com coluna `"metadata"` |
| `ame.db locked` | Feche outro processo ou `rm ame.db && python scripts/init_db.py` |
| Testes falhando por estado sujo | `rm ame.db ame_memory.json && python scripts/init_db.py && python scripts/seed.py` |

---

## 📜 Licença

MIT — Use, adapte, monetize. **FAZER > EXPLICAR.**

---

**Construído pelo AGENTE PRINCIPAL — Autonomous Builder.**  
*Transformar especificação em software funcional. Loop nunca termina; ao concluir tarefa → verificar resultado → registrar → atualizar memória → próxima ação.*

> `ANALISE → CONSTRUA → TESTE → CORRIJA → INTEGRE → VERSIONE → PUBLIQUE → MONITORE → MELHORE`
