# 💰 Repositório Central da Automação de Criar Dinheiro

> **Um ecossistema completo para automatizar suas fontes de renda online. Um só lugar, todas as automações.**

[![Status](https://img.shields.io/badge/status-em%20construção-yellow)]()
[![Python](https://img.shields.io/badge/Python-3.11+-blue)]()
[![Licença](https://img.shieldsio/badge/licença-MIT-green)]()
[![Foco](https://img.shields.io/badge/foco-renda%20passiva-success)]()

Este repositório foi criado para ser o **cérebro central** de todas as suas automações de geração de renda. Em vez de scripts espalhados, aqui tudo é organizado, documentado e pronto para escalar.

---

### 🎯 O que este repositório faz?

Ele centraliza 6 máquinas de dinheiro automatizadas:

| Máquina | O que automatiza | Potencial |
|---------|-----------------|-----------|
| **1. Afiliados Hotmart/Kiwify/Eduzz** | Garimpa produtos quentes, gera links, cria páginas de venda | R$ 100-500/dia |
| **2. Scraping Shopee/Amazon** | Monitora preços, encontra produtos virais, gera vídeos | R$ 50-300/dia |
| **3. Fábrica de Conteúdo com IA** | Gera posts, reels, scripts TikTok/YouTube Dark com ChatGPT | Tráfego infinito |
| **4. Bots WhatsApp/Telegram** | Atendimento, vendas, recuperação de carrinho 24h | +30% conversão |
| **5. Tráfego Automático** | Posta no Instagram, TikTok, Pinterest, X no piloto automático | Seguidores/vendas |
| **6. E-mail & Funil** | Sequência de e-mails que vende enquanto você dorme | LTV alto |

---

### 📁 Estrutura do Repositório

```
repositorio-cental-da-automa-o-de-criar-dinheiro/
├── 📂 automacoes/
│   ├── 01-afiliados/          → Garimpo e venda de produtos afiliados
│   ├── 02-scraping/           → Monitoramento Shopee/Amazon/Aliexpress
│   ├── 03-conteudo-ia/        → Geração de conteúdo com IA
│   ├── 04-bots/               → Bots WhatsApp e Telegram
│   ├── 05-trafego/            → Autopost em redes sociais
│   └── 06-email/              → Automação de e-mail marketing
├── 📂 dashboard/              → Painel central para ver ganhos
├── 📂 n8n-workflows/          → Workflows prontos para n8n
├── 📂 docs/                   → Documentação e tutoriais
├── 🤖 central.py              → Orquestrador principal (roda tudo)
├── ⚙️ .env.example            → Suas chaves de API
└── 🐳 docker-compose.yml      → Sobe tudo com 1 comando
```

---

### 🚀 Começo Rápido (3 minutos)

```bash
# 1. Clone
git clone https://github.com/po0258611-maker/repositorio-cental-da-automa-o-de-criar-dinheiro.git
cd repositorio-cental-da-automa-o-de-criar-dinheiro

# 2. Configure suas chaves
cp .env.example .env
# Edite o .env com suas chaves (OpenAI, Telegram, etc)

# 3. Instale
pip install -r requirements.txt

# 4. Rode a central
python central.py --menu
```

Ou com Docker (recomendado):
```bash
docker-compose up -d
# Acesse o dashboard em http://localhost:3000
# Acesse o n8n em http://localhost:5678
```

---

### 🧠 Como Usar a Central

O arquivo `central.py` é seu painel de controle:

```bash
python central.py --menu              # Menu interativo
python central.py --afiliados         # Roda garimpo de afiliados
python central.py --conteudo --tema "renda extra" --qtd 10
python central.py --scraping --loja shopee
python central.py --bot telegram
python central.py --trafego --rede instagram
python central.py --dashboard         # Abre o dashboard local
```

---

### 🔑 Configuração (.env)

Crie um arquivo `.env` baseado no `.env.example`:

```env
# IA
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# BOTS
TELEGRAM_BOT_TOKEN=...
WHATSAPP_TOKEN=...

# AFILIADOS
HOTMART_TOKEN=...
KIWIFY_TOKEN=...

# REDES SOCIAIS
INSTAGRAM_USER=...
TIKTOK_SESSION=...
```

---

### 📈 Roadmap

- [x] Estrutura central criada
- [x] Orquestrador `central.py`
- [x] Módulo Afiliados + Scraping
- [x] Fábrica de Conteúdo IA
- [x] Bots Telegram/WhatsApp
- [ ] Dashboard Web em React
- [ ] Integração n8n completa
- [ ] Módulo PLR Automático
- [ ] App Mobile de acompanhamento

---

### 🤝 Como Contribuir

Este é SEU repositório central. Adicione suas próprias automações em `automacoes/` e elas aparecerão automaticamente no menu da `central.py`.

### ⚠️ Aviso Legal

Automação é ferramenta. Resultado depende de estratégia, consistência e tráfego. Este repo não promete dinheiro fácil, mas te dá as FERRAMENTAS para automatizar o trabalho duro.

---

**Criado por [@po0258611-maker](https://github.com/po0258611-maker) | Salvador, Bahia 🇧🇷**

> *"Automatize o trabalho, escale os ganhos."*

**Próximo passo:** Escolha uma automação abaixo e comece hoje. Qual você quer ativar primeiro?
