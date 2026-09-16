# Workflows n8n - Central da Automação

Arraste estes JSONs para dentro do seu n8n (http://localhost:5678) após rodar `docker-compose up`.

### Workflows incluídos:

1. **afiliados-garimpo.json** - Roda todo dia 08:00, busca produtos quentes e te envia no Telegram
2. **conteudo-autopost.json** - Gera 3 posts com IA todo dia 07:00 e agenda no Instagram
3. **bot-recuperacao.json** - Quando lead abandona, envia mensagem no WhatsApp em 30min
4. **email-funil.json** - Sequência de 7 e-mails após cadastro

> Para criar: n8n -> Import from File -> selecione o .json -> Configure suas credenciais (Telegram, OpenAI, etc) -> Activate

Em breve os arquivos .json completos estarão aqui. Por enquanto use os scripts Python em `/automacoes` que já fazem o mesmo.
