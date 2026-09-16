# 📘 Guia Rápido - Central da Automação

## 1. Para quem é?
- Afiliados Hotmart/Kiwify/Eduzz
- Quem vende na Shopee/Amazon como afiliado
- Criadores de conteúdo dark / faceless
- Quem quer renda extra automatizada

## 2. Instalação em 3 passos

```bash
git clone https://github.com/po0258611-maker/repositorio-cental-da-automa-o-de-criar-dinheiro.git
cd repositorio-cental-da-automa-o-de-criar-dinheiro
python -m venv .venv && source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# edite o .env
python central.py --menu
```

## 3. Fluxo recomendado para iniciantes

**Semana 1 - Garimpo**
1. `python central.py --afiliados` -> escolha 2 produtos com comissão >65%
2. Peça afiliação (Hotmart/Kiwify aprova em até 48h)
3. `python central.py --conteudo --tema "nome do produto" --qtd 10`

**Semana 2 - Tráfego**
4. Configure Instagram secundário
5. `python central.py --trafego` -> agende 2 posts/dia
6. Ative o bot: `python central.py --bot telegram` (precisa do token do @BotFather)

**Semana 3 - Vendas**
7. Crie funil de e-mail: `python central.py` -> opção 6
8. Coloque link da bio com seu link de afiliado
9. Acompanhe no dashboard: `python dashboard/app.py`

## 4. Sem API paga, funciona?
Sim! Todos os módulos têm MODO DEMO/TEMPLATE que funciona offline.
Quando quiser escalar, adicione:
- OpenAI: $5 já gera 500+ posts
- Telegram: 100% grátis
- n8n: grátis self-hosted

## 5. Dúvidas frequentes

**Preciso aparecer?** Não. Módulo de conteúdo gera roteiros faceless (voz IA + stock).

**Preciso investir?** Pode começar 100% orgânico. Tráfego pago é opcional.

**Quanto tempo por dia?** Após configurar, 30min/dia para revisar e responder leads. O resto é automático.

## 6. Próximos passos
- Leia `automacoes/*/README.md` de cada módulo
- Veja o dashboard em http://localhost:8000
- Entre no canal do Telegram (configure no .env)

Bons lucros! 💰
