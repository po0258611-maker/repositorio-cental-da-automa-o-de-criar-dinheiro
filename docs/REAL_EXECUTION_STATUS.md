# AME — Estado de Execução Real

## Objetivo

O AME agora diferencia explicitamente execução real, demonstração e recurso não configurado.

> Dados e ações externas só podem ser tratados como reais quando foram obtidos/executados por um provider configurado e o resultado foi confirmado.

## O que foi convertido

- Pesquisa web: provider Tavily/Serper.
- Busca/extração de URL: HTTP real.
- LLM: mock não é mais silencioso em produção/execução real.
- Criação de arquivos: restrita ao workspace.
- Telegram: envio real pela Bot API quando configurado.
- Campanhas de marketing: persistidas no banco.
- Funil de vendas: usa leads e vendas observados no banco; não fabrica conversões.
- Tasks: execução passou a usar worker persistente baseado na tabela tasks.
- Recuperação: tasks running antigas podem retornar para pending.
- Financeiro: receitas/despesas passaram a ser persistidas na tabela transactions.

## Variáveis

### Execução

- `AME_REAL_EXECUTION=true`
- `AME_ALLOW_MOCKS=false`

Em produção, mocks ficam desativados automaticamente.

### Pesquisa

- `TAVILY_API_KEY`
- `SERPER_API_KEY`
- `AME_RESEARCH_PROVIDER=tavily`

Sem provider configurado, pesquisa retorna `NOT_CONFIGURED`.

### Telegram

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Sem configuração, o envio retorna `NOT_CONFIGURED`.

## Estados importantes

O sistema deve diferenciar:

- `OK` — operação executada.
- `NOT_CONFIGURED` — recurso exige configuração.
- `ERROR` — integração configurada, mas falhou.
- `INSUFFICIENT_EVIDENCE` — não há evidência suficiente para decisão.
- `MOCK` — somente permitido explicitamente fora de produção/execução real.

## Limitações ainda abertas

1. Ledger financeiro ainda precisa de migração monetária completa para NUMERIC/Decimal.
2. Worker atual é polling em processo; o próximo estágio é Redis/queue + workers independentes.
3. Research precisa de Evidence Store persistente dedicado.
4. Checkout/pagamento real ainda depende da integração do provedor.
5. Ads/social/email ainda precisam de adapters reais por plataforma.
6. RBAC/Policy Engine completo ainda está em evolução.
7. CI do commit atual ainda precisa de execução verificável; a consulta ao status do commit não retornou checks publicados.

## Regra MVP

Toda alteração estrutural futura deve ser sincronizada com o MVP existente, preservando endpoints, modelos, agentes, dashboard e inicialização ou fornecendo uma migração explícita.