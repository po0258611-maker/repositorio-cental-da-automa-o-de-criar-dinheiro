# AME — AUDITORIA, ARQUITETURA-ALVO E PLANO COMPLETO

**Projeto:** Autonomous Money Engine (AME)  
**Repositório:** `po0258611-maker/repositorio-cental-da-automa-o-de-criar-dinheiro`  
**Data da consolidação:** 2026-09-16  
**Objetivo:** centralizar em um único documento a auditoria técnica realizada, os problemas encontrados, a arquitetura-alvo, funcionalidades recomendadas, integrações e plano de reconstrução/evolução.

---

## 1. VISÃO EXECUTIVA

O AME deve ser tratado como uma **plataforma de execução empresarial autônoma orientada a resultado econômico**, e não como um simples chatbot ou coleção de automações.

Fluxo econômico central:

```text
OBSERVE
→ RESEARCH
→ DISCOVER
→ VALIDATE
→ DECIDE
→ BUILD
→ PUBLISH
→ DISTRIBUTE
→ SELL
→ MEASURE
→ LEARN
→ OPTIMIZE
→ REINVEST
→ REPEAT
```

A meta operacional é maximizar **lucro líquido sustentável**, considerando custo, risco, capacidade técnica, regras das plataformas e controles humanos.

O sistema deve combinar:

- multi-agent orchestration;
- internet research;
- ferramentas externas;
- workflows duráveis;
- memória persistente;
- evidence/knowledge engine;
- economic engine;
- product factory;
- growth/sales engine;
- observabilidade;
- auditabilidade;
- self-healing;
- governança e human override.

---

# 2. AUDITORIA DO ESTADO ATUAL DO REPOSITÓRIO

## 2.1 O que foi efetivamente encontrado no `main`

A árvore Git observada contém:

```text
.env.example
.gitignore
Dockerfile
MASTER_INSTRUCTIONS.md
README.md
ame (1) (1).zip
ame (1).zip
central.py
docker-compose.yml
pytest.ini
requirements.txt
```

Existem dois ZIPs com o mesmo conteúdo/hash aparente. O conteúdo binário interno dos ZIPs não pôde ser auditado pelo conector GitHub utilizado nesta revisão; portanto, esta auditoria distingue explicitamente o que está versionado como código acessível do que está apenas dentro do ZIP.

## 2.2 Inconsistência crítica entre README e árvore real

O README descreve diretórios e módulos que não estão presentes na árvore Git observada, incluindo:

```text
app/
app/core/
app/models/
app/agents/
app/providers/
app/services/
app/api/
automacoes/
dashboard/
scripts/
tests/
```

O README também declara 27 agentes e estado de produção.

### Conclusão

A documentação descreve uma arquitetura mais completa do que aquela efetivamente presente no `main`.

Não considerar o README como prova de implementação.

Regra obrigatória para o Builder Agent:

```text
VERIFY REPOSITORY REALITY
≠
TRUST DOCUMENTATION
```

---

# 3. BLOQUEADOR DE EXECUÇÃO ATUAL

O `Dockerfile` executa:

```text
python scripts/init_db.py
python scripts/seed.py
```

e depois inicia:

```text
uvicorn app.main:app
```

Porém esses caminhos não aparecem na árvore Git atual.

Portanto, **não há evidência suficiente para declarar o repositório atual como uma aplicação de produção funcional de ponta a ponta**.

O README deve deixar de afirmar `Status: Produção` até que build, testes, health checks, deploy e smoke tests sejam efetivamente comprovados.

---

# 4. PONTOS POSITIVOS DA CONCEPÇÃO

Apesar da inconsistência de implementação, a arquitetura conceitual já possui vários elementos corretos.

## 4.1 Multi-agent por domínio

A divisão por:

- research;
- product;
- creative;
- growth;
- finance;
- quality;
- learning;

é adequada.

## 4.2 Orchestrator

A ideia de seleção dinâmica de agentes por missão deve ser mantida.

## 4.3 Economic Engine

A ideia de medir:

- receita;
- despesa;
- lucro;
- margem;
- ROI;
- ROAS;
- CAC;
- LTV;
- runway;

é essencial.

## 4.4 Experiment Engine

Cada iniciativa de negócio deve ser um experimento mensurável.

## 4.5 Memória

Memória de sucessos, falhas, produtos, mercado e finanças é necessária para evitar repetição cega.

## 4.6 Provider abstraction

Separar LLM, imagem, vídeo, documentos e browser por adapters/providers é uma boa decisão arquitetural.

## 4.7 Human Override

Autonomia deve coexistir com:

```text
PAUSE
STOP
OVERRIDE
BUDGET_LIMIT
SPENDING_LIMIT
RISK_LIMIT
APPROVAL_REQUIRED
```

---

# 5. PROBLEMAS PRIORITÁRIOS A CORRIGIR

## P0 — Repositório/documentação inconsistente

**Problema:** README descreve módulos não presentes no Git.

**Ação:** reconciliar código real e documentação antes de declarar qualquer feature pronta.

## P0 — Docker não corresponde à árvore atual

**Problema:** Dockerfile referencia `app.main` e `scripts/*` inexistentes no `main` observado.

**Ação:** reconstruir os diretórios reais ou alinhar Docker ao código que efetivamente será mantido.

## P0 — Produção não comprovada

**Problema:** badge/documentação de produção sem evidência de pipeline CI/CD e smoke test real.

**Ação:** só declarar produção após pipeline verificável.

## P0 — Credencial padrão exposta em docker-compose

O compose contém credencial fixa de n8n:

```text
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=central123
```

**Ação:** mover para variável de ambiente e exigir secret em ambiente real.

## P1 — `central.py` ainda representa a geração legada

O arquivo funciona como menu/dispatcher das automações antigas, em vez de ser um verdadeiro cérebro econômico.

**Ação:** converter automações existentes em `tools` e adapters controlados pelo Orchestrator.

## P1 — Dependências excessivamente agregadas

O `requirements.txt` mistura IA, API, bots, scraping, email, planilhas, observabilidade e outros domínios.

**Ação:** separar dependências essenciais, providers opcionais e integrações opcionais.

## P1 — SQLite como padrão de produção

SQLite é adequado para desenvolvimento, mas a operação contínua deve utilizar PostgreSQL.

**Política:**

```text
Development → SQLite
Production   → PostgreSQL
```

## P1 — Ausência comprovada de CI/CD

Não assumir pipeline funcional até que exista e execute.

## P1 — Ausência de durable execution

Workflows não podem depender da memória de processo.

**Ação:** persistir estado de tarefas e workflows.

## P1 — Ausência de Tool Gateway centralizado

Agentes não devem chamar APIs sensíveis diretamente.

**Ação:**

```text
Agent
→ Tool Gateway
→ Policy Engine
→ Risk Check
→ Budget Check
→ Credential Check
→ Execute
→ Audit
```

## P1 — Falta de Evidence Engine

Decisões de negócio precisam apontar para evidências rastreáveis.

## P1 — Falta de self-healing robusto

Adicionar retry, fallback, circuit breaker, rollback e escalation.

## P2 — Falta de Agent Performance Engine

Medir desempenho dos agentes individualmente.

## P2 — Falta de sandbox por agente/job

Agentes de maior risco devem executar em ambientes isolados.

---

# 6. ARQUITETURA-ALVO

A arquitetura final recomendada possui 10 camadas:

```text
┌─────────────────────────────────────────────┐
│ 10. HUMAN CONTROL / GOVERNANCE             │
├─────────────────────────────────────────────┤
│ 9. OBSERVABILITY / AUDIT / METRICS         │
├─────────────────────────────────────────────┤
│ 8. ECONOMIC ENGINE                         │
├─────────────────────────────────────────────┤
│ 7. MEMORY / KNOWLEDGE / RAG                │
├─────────────────────────────────────────────┤
│ 6. AGENT ORCHESTRATION                     │
├─────────────────────────────────────────────┤
│ 5. WORKFLOW / TASK GRAPH / SCHEDULER       │
├─────────────────────────────────────────────┤
│ 4. TOOL GATEWAY / POLICY ENGINE            │
├─────────────────────────────────────────────┤
│ 3. INTERNET / INTEGRATIONS                  │
├─────────────────────────────────────────────┤
│ 2. BUSINESS DOMAIN                          │
├─────────────────────────────────────────────┤
│ 1. DATA / STORAGE                           │
└─────────────────────────────────────────────┘
```

---

# 7. ESTRUTURA DE DIRETÓRIOS-ALVO

```text
AME/
│
├── apps/
│   ├── api/
│   ├── dashboard/
│   └── worker/
│
├── ame/
│   ├── core/
│   │   ├── config/
│   │   ├── lifecycle/
│   │   ├── events/
│   │   ├── policies/
│   │   ├── security/
│   │   └── observability/
│   │
│   ├── orchestration/
│   │   ├── orchestrator/
│   │   ├── planner/
│   │   ├── scheduler/
│   │   ├── task_graph/
│   │   ├── state_machine/
│   │   └── recovery/
│   │
│   ├── agents/
│   │   ├── research/
│   │   ├── product/
│   │   ├── creative/
│   │   ├── growth/
│   │   ├── finance/
│   │   ├── quality/
│   │   └── learning/
│   │
│   ├── tools/
│   │   ├── gateway/
│   │   ├── registry/
│   │   ├── policies/
│   │   └── sandbox/
│   │
│   ├── internet/
│   │   ├── search/
│   │   ├── browser/
│   │   ├── http/
│   │   ├── webhooks/
│   │   └── extraction/
│   │
│   ├── integrations/
│   │   ├── llm/
│   │   ├── image/
│   │   ├── video/
│   │   ├── payments/
│   │   ├── social/
│   │   ├── email/
│   │   ├── crm/
│   │   ├── marketplaces/
│   │   └── storage/
│   │
│   ├── economy/
│   │   ├── treasury/
│   │   ├── accounting/
│   │   ├── unit_economics/
│   │   ├── experiments/
│   │   └── scoring/
│   │
│   ├── memory/
│   │   ├── episodic/
│   │   ├── semantic/
│   │   ├── procedural/
│   │   └── knowledge/
│   │
│   ├── evidence/
│   │   ├── sources/
│   │   ├── claims/
│   │   └── verification/
│   │
│   ├── products/
│   │   ├── factory/
│   │   ├── catalog/
│   │   ├── offers/
│   │   └── publishing/
│   │
│   ├── growth/
│   │   ├── acquisition/
│   │   ├── campaigns/
│   │   ├── content/
│   │   ├── seo/
│   │   └── attribution/
│   │
│   └── audit/
│       ├── ledger/
│       ├── actions/
│       └── compliance/
│
├── database/
│   ├── migrations/
│   ├── models/
│   └── repositories/
│
├── workers/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── security/
│   └── economic/
│
├── docs/
│   ├── architecture/
│   ├── agents/
│   ├── integrations/
│   ├── governance/
│   └── operations/
│
├── infra/
│   ├── docker/
│   ├── monitoring/
│   └── deployment/
│
└── .github/
    └── workflows/
```

---

# 8. AGENTES

## Orquestração

- ORCHESTRATOR_AGENT
- DECISION_AGENT
- SCHEDULER_AGENT

## Inteligência de mercado

- MARKET_AGENT
- TREND_AGENT
- COMPETITOR_AGENT
- VALIDATION_AGENT
- WEB_RESEARCH_AGENT

## Produto

- PRODUCT_STRATEGIST_AGENT
- PRODUCT_BUILDER_AGENT
- DIGITAL_PRODUCT_AGENT
- LANDING_PAGE_AGENT

## Criação

- COPY_AGENT
- CONTENT_AGENT
- IMAGE_AGENT
- VIDEO_AGENT

## Crescimento

- SEO_AGENT
- SOCIAL_AGENT
- ADS_AGENT
- EMAIL_AGENT
- SALES_AGENT

## Finanças

- CFO_AGENT
- ECONOMIC_AGENT
- PRICING_AGENT
- TREASURY_AGENT

## Qualidade e segurança

- QA_AGENT
- SECURITY_AGENT
- RISK_AGENT
- COMPLIANCE_AGENT

## Aprendizado

- ANALYTICS_AGENT
- EXPERIMENT_AGENT
- LEARNING_AGENT
- AGENT_PERFORMANCE_AGENT

---

# 9. INTERNET ENGINE

O AME deve ter conexão real com a internet por uma camada própria.

Fluxo:

```text
SEARCH
→ FETCH
→ PARSE
→ EXTRACT
→ NORMALIZE
→ VERIFY
→ STORE
→ CITE
```

Capacidades:

- web search;
- HTTP fetch;
- browser automation;
- parsing;
- scraping responsável;
- monitoramento de páginas;
- webhooks;
- APIs externas;
- coleta de sinais de mercado;
- coleta de preços;
- pesquisa de concorrência;
- leitura de documentação.

Criar adapters para provedores de busca e browser.

---

# 10. EVIDENCE ENGINE

Toda decisão econômica importante deve poder apontar para uma evidência.

Estrutura mínima de uma evidência:

```json
{
  "claim": "...",
  "source": "...",
  "published_at": "...",
  "retrieved_at": "...",
  "confidence": 0.0,
  "evidence_type": "market_data",
  "supports": "experiment-id"
}
```

Benefícios:

- auditabilidade;
- redução de alucinação;
- melhor decisão de mercado;
- rastreabilidade;
- atualização de informação.

---

# 11. WORKFLOW ENGINE

Nunca depender apenas de chamadas síncronas entre agentes.

Usar Task Graph.

Exemplo:

```text
Research
  ↓
Validation
  ↓
Offer
  ↓
Product
  ├── Ebook
  ├── Landing
  └── Creative
          ↓
       Publish
          ↓
       Traffic
          ↓
       Sales
          ↓
       Analytics
```

Cada tarefa deve guardar:

- task_id;
- parent_id;
- experiment_id;
- agent;
- tool;
- input;
- output;
- status;
- retries;
- cost;
- duration;
- risk;
- timestamps.

---

# 12. DURABLE EXECUTION

O estado precisa sobreviver a:

- restart;
- crash;
- timeout;
- mudança de modelo;
- falha de API;
- deploy;
- interrupção de processo.

Exemplo de estado persistente:

```text
Experiment 104
Status: BUILDING
Last successful step: PRODUCT_CONTENT
Next step: IMAGE_GENERATION
Retry: 2/5
```

---

# 13. TOOL GATEWAY

Todos os agentes passam por um gateway central de ferramentas.

```text
Agent
 ↓
Tool Gateway
 ↓
Policy Engine
 ↓
Risk Classifier
 ↓
Budget Check
 ↓
Credential Check
 ↓
Execution
 ↓
Audit
```

Cada tool declara:

- name;
- input schema;
- output schema;
- cost;
- risk;
- timeout;
- retry policy;
- approval requirement;
- required permissions.

---

# 14. SECURITY / SANDBOX

Agentes e jobs de maior risco devem ter isolamento quando possível.

Controles:

- filesystem sandbox;
- network policy;
- CPU limit;
- memory limit;
- allowed tools;
- allowed secrets;
- timeout;
- kill switch.

Nunca expor:

- API keys;
- tokens;
- senhas;
- private keys;
- secrets.

---

# 15. ECONOMIC ENGINE AVANÇADO

Além de receita/despesa/lucro, monitorar:

- CAC;
- LTV;
- ARPU;
- AOV;
- gross_margin;
- contribution_margin;
- payback_period;
- ROAS;
- ROI;
- refund_rate;
- churn;
- retention;
- conversion_rate.

Criar:

```text
Economic Value Per Agent Hour
```

para identificar quais atividades geram mais valor por recurso consumido.

---

# 16. TREASURY

Criar bolsões internos configuráveis:

```text
operating
experimentation
marketing
reserve
emergency
```

As regras de alocação devem ser configuráveis e nunca hard-coded de forma irreversível.

---

# 17. BUSINESS HEALTH

Monitorar:

```text
financial_health
product_health
marketing_health
technical_health
customer_health
strategic_health
```

Estados:

```text
EXPANSION
GROWTH
OPTIMIZATION
SURVIVAL
EMERGENCY
```

O “modo morte” deve significar arquivamento da iniciativa, nunca autodestruição do sistema.

---

# 18. SELF-HEALING ENGINE

Fluxo:

```text
Detect
→ Diagnose
→ Retry
→ Fallback
→ Rollback
→ Escalate
```

Problemas monitorados:

- API down;
- database error;
- model rate limit;
- invalid output;
- timeout;
- webhook failure;
- budget exceeded;
- bad deploy;
- regression.

---

# 19. MODEL ROUTER

O AME deve ser multi-provider.

Critérios:

- custo;
- qualidade;
- latência;
- complexidade;
- disponibilidade;
- quota.

O router deve ter:

- provider failover;
- quota tracking;
- token accounting;
- model health;
- pricing table;
- retry policy.

---

# 20. MCP / TOOL REGISTRY

Adicionar compatibilidade com registry de ferramentas/MCP quando apropriado.

Objetivo:

- conectar GitHub;
- conectar storage;
- conectar CRM;
- conectar browser;
- conectar analytics;
- conectar pagamentos;
- conectar documentos;
- conectar serviços externos;

sem acoplar o Orchestrator a cada API individualmente.

---

# 21. MEMORY + KNOWLEDGE ENGINE

Separar:

## Memória episódica

O que aconteceu.

## Memória semântica

O que o sistema sabe.

## Memória procedural

Como executar.

## Knowledge base

Documentos, fontes, pesquisas e políticas.

Categorias mínimas:

- market_memory;
- product_memory;
- customer_memory;
- marketing_memory;
- financial_memory;
- experiment_memory;
- failure_memory;
- success_memory;
- system_memory.

Adicionar RAG/vector search quando houver necessidade real.

---

# 22. AGENT PERFORMANCE ENGINE

Métricas por agente:

- success_rate;
- failure_rate;
- avg_cost;
- avg_latency;
- retry_rate;
- QA score;
- revenue impact;
- task completion;
- regression rate.

Criar um `Agent Performance Score` para permitir roteamento e otimização futuros.

---

# 23. AUDIT LEDGER

Criar trilha de auditoria append-only.

Campos sugeridos:

```text
agent
 timestamp
tool
input_hash
output_hash
cost
risk
decision
result
previous_event_hash
current_event_hash
```

O objetivo é poder reconstruir quem fez o quê, quando, com qual ferramenta, custo e resultado.

---

# 24. PRODUCT FACTORY

Capacidade para criar:

- ebooks;
- PDFs;
- templates;
- checklists;
- planilhas;
- prompts;
- páginas;
- sites;
- criativos;
- imagens;
- vídeos;
- ferramentas;
- micro-SaaS;
- produtos digitais;
- serviços produtizados.

Todo produto deve possuir:

- público;
- problema;
- solução;
- proposta de valor;
- oferta;
- preço;
- custo;
- canais;
- métricas;
- status.

---

# 25. GROWTH ENGINE

Adicionar:

- acquisition;
- content;
- SEO;
- campaign management;
- attribution;
- email;
- social;
- ad experiments;
- lead scoring;
- funnel analytics.

A atribuição deve conectar:

```text
conteúdo
→ visita
→ lead
→ oferta
→ venda
→ receita
```

---

# 26. INTEGRAÇÕES

Arquitetura preparada para:

## IA

- OpenAI;
- Anthropic;
- Gemini;
- outros providers.

## Imagem/Vídeo

- providers intercambiáveis.

## Pesquisa/Web

- search APIs;
- browser automation;
- HTTP clients.

## Pagamentos

- Stripe;
- gateways/checkout utilizados pelo projeto;
- webhooks.

## Marketplaces/Afiliados

Somente por APIs ou mecanismos permitidos pelas respectivas plataformas.

## Comunicação

- email;
- Telegram;
- WhatsApp via APIs apropriadas;
- Slack/integrações empresariais.

## Analytics

- eventos próprios;
- analytics externos.

## Storage

- object storage;
- backup;
- exportação.

---

# 27. DATABASE

Desenvolvimento:

```text
SQLite
```

Produção:

```text
PostgreSQL
```

Entidades mínimas:

```text
users
agents
agent_runs
tasks
projects
experiments
products
offers
campaigns
leads
customers
sales
transactions
expenses
metrics
events
memory
evidence
integrations
api_usage
audit_events
system_settings
```

---

# 28. QUEUE / WORKERS

Adicionar uma camada de filas para:

- jobs;
- retries;
- locks;
- scheduling;
- rate limit distribuído;
- eventos;
- execução assíncrona.

Redis pode ser utilizado como infraestrutura auxiliar quando fizer sentido.

Separação lógica recomendada:

```text
API
Queue
Workers
Agent Runtime
Scheduler
Dashboard
```

---

# 29. DASHBOARD / MISSION CONTROL

O dashboard deve mostrar:

## Financeiro

- saldo;
- receita;
- despesa;
- lucro;
- margem;
- burn;
- runway;
- ROI;
- ROAS.

## Negócios

- produtos;
- experimentos;
- leads;
- vendas;
- conversão;
- CAC;
- LTV.

## Sistema

- agentes;
- jobs;
- erros;
- custos de IA;
- latência;
- integrações;
- saúde.

## Mission Control

- objetivo atual;
- missão ativa;
- plano atual;
- tarefas;
- agentes envolvidos;
- ferramentas utilizadas;
- custo;
- resultado;
- próxima ação.

---

# 30. FUNCIONALIDADES ADICIONAIS RECOMENDADAS

## Autonomy Readiness

Medir maturidade do sistema em dimensões como:

- internet;
- tools;
- memory;
- economy;
- observability;
- safety;
- self-healing.

## Agent Doctor

Diagnóstico automático de:

- APIs;
- database;
- modelos;
- workers;
- browser;
- payments;
- storage;
- webhooks.

## Dry Run

Simular operações sem executá-las:

- ações;
- custo esperado;
- risco;
- valor esperado.

## Shadow Mode

Planejar e observar sem executar externamente até atingir condições configuradas.

## Replay

Reexecutar um experimento anterior em ambiente de teste.

## Strategy Simulator

Simular mudanças de preço, canal, orçamento e oferta sem gastar dinheiro real.

## Experiment Laboratory

Executar experimentos isolados em paralelo.

## Revenue Attribution

Relacionar conteúdo, campanhas, canais, produtos e receita.

## Economic Kill Switch

Interromper automaticamente operações quando perda projetada ultrapassar um limite definido.

---

# 31. GITHUB / VERSIONAMENTO

Fluxo:

```text
ANALYZE
→ BRANCH
→ IMPLEMENT
→ TEST
→ FIX
→ COMMIT
→ PUSH
→ CI
→ VERIFY
→ PR/MERGE
```

Commits semânticos:

```text
feat:
fix:
refactor:
test:
docs:
chore:
perf:
security:
```

Nunca usar force-push em branch compartilhada sem necessidade operacional legítima.

Não usar exclusão do repositório como mecanismo de recuperação.

---

# 32. CI/CD

Criar pipeline com pelo menos:

```text
lint
↓
type checks
↓
unit tests
↓
integration tests
↓
security checks
↓
build
↓
container test
↓
smoke test
```

Só marcar `production` depois de evidência verificável.

---

# 33. TESTES

Obrigatórios conforme aplicável:

- unit;
- integration;
- API;
- database;
- workflow;
- E2E;
- security;
- economic;
- smoke;
- regression.

Quando falhar:

```text
REPRODUZIR
→ IDENTIFICAR
→ CORRIGIR
→ TESTAR
→ REGRESSÃO
```

---

# 34. SECURITY HARDENING

Corrigir imediatamente:

1. credenciais fixas no `docker-compose.yml`;
2. segredos default como `change-me` em ambientes reais;
3. CORS permissivo em produção;
4. rate limiting distribuído;
5. secrets manager;
6. webhook signature validation;
7. idempotency keys em pagamentos;
8. audit logging;
9. least privilege;
10. proteção de ferramentas de alto risco.

---

# 35. SELF-SERVICE OPERATION

O sistema deve procurar automaticamente a próxima ação útil após terminar uma tarefa.

Regra:

```text
ACTION
→ RESULT
→ METRIC
→ LESSON
→ NEXT_ACTION
```

Não entrar em loop de planejamento sem execução.

---

# 36. BUILDER AGENT — REGRA DE RECONCILIAÇÃO

O agente responsável por construir o projeto deve seguir esta ordem:

```text
1. VERIFY REPOSITORY REALITY
2. INVENTORY FILES
3. INSPECT ZIP/LEGACY ASSETS WHEN POSSIBLE
4. RECONCILE DOCUMENTATION
5. DEFINE SOURCE OF TRUTH
6. CREATE ARCHITECTURE RECORD
7. IMPLEMENT FOUNDATIONAL LAYERS
8. TEST
9. FIX
10. CONTINUE
```

A documentação nunca deve ser tomada como prova de que uma feature existe.

---

# 37. FASES DE IMPLEMENTAÇÃO

## FASE 0 — Reconciliação

- reconciliar ZIP e Git;
- decidir o que é legado;
- estabelecer source of truth;
- corrigir README.

## FASE 1 — Base executável

- criar estrutura real;
- FastAPI;
- config;
- health;
- logging;
- tests;
- Docker.

## FASE 2 — Dados e workers

- PostgreSQL;
- migrations;
- repositories;
- queue;
- worker;
- scheduler.

## FASE 3 — Orchestrator

- planner;
- state machine;
- task graph;
- durable execution.

## FASE 4 — Tools + Internet

- tool gateway;
- policies;
- search;
- browser;
- webhooks;
- integrations.

## FASE 5 — Agent Runtime

- agents;
- routing;
- model router;
- permissions.

## FASE 6 — Economic Engine

- treasury;
- accounting;
- experiments;
- scoring;
- unit economics.

## FASE 7 — Memory + Evidence

- episodic;
- semantic;
- procedural;
- RAG;
- evidence.

## FASE 8 — Product Factory

- digital products;
- creative generation;
- landing pages;
- publishing.

## FASE 9 — Growth + Sales

- content;
- acquisition;
- email;
- social;
- lead management;
- payments;
- attribution.

## FASE 10 — Reliability

- self-healing;
- retries;
- fallback;
- rollback;
- provider failover;
- chaos/smoke testing.

## FASE 11 — Governance

- human override;
- approval queue;
- audit ledger;
- risk engine;
- policy engine.

## FASE 12 — Production

- CI/CD;
- deployment;
- observability;
- health verification;
- documentation final.

---

# 38. DEFINITION OF DONE

Uma funcionalidade só pode ser declarada concluída quando:

- código implementado;
- testes apropriados executados;
- integrações verificadas;
- logs disponíveis;
- métricas disponíveis quando relevantes;
- documentação atualizada;
- estado persistido;
- segurança revisada;
- versionamento realizado;
- smoke test concluído quando aplicável.

---

# 39. CRITÉRIO PARA DECLARAR PRODUÇÃO

Só usar `production` quando:

1. build reproduzível;
2. CI verde;
3. database migration verificada;
4. health check funcionando;
5. smoke test funcionando;
6. secrets configurados corretamente;
7. logs e métricas funcionando;
8. rollback disponível;
9. integrações críticas verificadas;
10. caminho de recuperação validado.

---

# 40. REFERÊNCIAS DE PADRÕES UTILIZADOS

A arquitetura foi comparada com padrões observados em projetos atuais de agentes autônomos, incluindo:

- autonomous AI agencies;
- autonomous business operating systems;
- AI company operating systems;
- agent runtimes com sandbox;
- durable workflow systems;
- multi-agent message buses;
- RAG/knowledge architectures;
- agent performance/reward systems;
- observability e audit logging para agentes.

Padrões extraídos:

- durable execution;
- plan → execute → verify;
- provider failover;
- human approval queues;
- sandbox isolation;
- performance scoring;
- self-healing;
- event-driven orchestration;
- append-only audit;
- tool registries;
- knowledge/RAG;
- business/economic loops.

Essas referências servem como inspiração arquitetural e não devem ser copiadas cegamente.

---

# 41. PRINCÍPIOS FINAIS DO AME

```text
FAZER > EXPLICAR

EVIDÊNCIA > OPINIÃO

RESULTADO > ATIVIDADE

LUCRO > FATURAMENTO

EXPERIMENTO > ACHISMO

REUTILIZAR > REESCREVER SEM NECESSIDADE

OBSERVAR > ASSUMIR

VERIFICAR > DECLARAR

PAUSAR > DESTRUIR

AUTONOMIA + GOVERNANÇA > AUTONOMIA IRRESTRITA
```

O sistema deve ser construído como uma **plataforma de execução econômica durável, observável, auditável, integrada à internet e evolutiva**.

O objetivo final não é possuir muitos agentes.

O objetivo é possuir um sistema capaz de:

```text
DESCUBRIR
→ VALIDAR
→ DECIDIR
→ EXECUTAR
→ MEDIR
→ APRENDER
→ CORRIGIR
→ ESCALAR
```

de forma contínua, controlada e economicamente mensurável.

---

# 42. ORDEM FINAL PARA O BUILDER AGENT

Ao receber este documento:

```text
DO NOT ASSUME.
DO NOT TRUST UNVERIFIED DOCUMENTATION.
DO NOT STOP AT PLANNING.
DO NOT DECLARE PRODUCTION WITHOUT PROOF.
DO NOT ASK THE HUMAN TO DO WORK YOU CAN EXECUTE.

VERIFY.
RECONCILE.
BUILD.
TEST.
FIX.
VERSION.
VERIFY AGAIN.
CONTINUE.
```

**Este documento é a fonte central de planejamento técnico e arquitetura para a evolução do AME.**
