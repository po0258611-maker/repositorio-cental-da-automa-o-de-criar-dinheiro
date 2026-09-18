# 💰 AUTONOMOUS MONEY ENGINE — AME

> Plataforma de automação empresarial orientada à geração de receita. Loop autônomo que pensa, planeja, constrói, vende, mede, aprende e reinveste.

[![AME Version](https://img.shields.io/badge/AME-v1.0.0-00d084?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)]()
[![License](https://img.shields.io/badge/Licença-MIT-green?style=flat-square)]()
[![Agents](https://img.shields.io/badge/Agentes-27-8a2be2?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Em%20valida%C3%A7%C3%A3o-yellow?style=for-the-badge)]()

**Repositório:** `po0258611-maker/repositorio-cental-da-automa-o-de-criar-dinheiro`  
**Branch principal:** `main`

## Estado técnico

O AME possui uma base multiagente e uma API FastAPI, mas a maturidade de produção ainda está em validação. O status de produção só deverá ser promovido após build, testes, smoke tests, verificação das integrações, segurança, persistência, observabilidade e deploy verificáveis.

Fluxo objetivo:

**OBSERVE → RESEARCH → DISCOVER → VALIDATE → DECIDE → BUILD → PUBLISH → DISTRIBUTE → SELL → MEASURE → LEARN → OPTIMIZE → REINVEST → REPEAT**

## Execução

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health:

```bash
curl http://localhost:8000/health
```

Documentação da API:

`http://localhost:8000/docs`

## Desenvolvimento

O projeto segue uma arquitetura modular com agentes especializados, API, persistência, ferramentas, observabilidade, camada econômica, experimentos, memória e integrações. O objetivo da próxima etapa é consolidar execução durável, queue/workers, internet engine, evidence engine, tool gateway, self-healing, auditoria e hardening de produção.

## Segurança

Não use secrets reais no repositório. Configure `.env` localmente ou um secret manager. O serviço n8n exige credenciais definidas no ambiente; não há senha padrão versionada.

## Regra de verdade operacional

A documentação deve refletir somente o que existe e foi verificado no código. Funcionalidade declarada, mas não executável ou não testada, deve ser tratada como pendência.

## Execução real (atual)

A base do MVP já possui execução real condicionada a providers configurados. Pesquisa web usa Tavily/Serper; tarefas podem ser processadas pelo worker persistente; campanhas são persistidas; vendas observadas não são mais inventadas; receitas e despesas são gravadas em `transactions`.

Para ativar o modo real:

```env
AME_REAL_EXECUTION=true
AME_ALLOW_MOCKS=false
TAVILY_API_KEY=
SERPER_API_KEY=
```

Consulte `docs/REAL_EXECUTION_STATUS.md` para o estado exato, limitações e integrações ainda pendentes.

**Regra:** uma integração sem credencial/configuração deve retornar `NOT_CONFIGURED` ou `ERROR`; não deve simular sucesso.
