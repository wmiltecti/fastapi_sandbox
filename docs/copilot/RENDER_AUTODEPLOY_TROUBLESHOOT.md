Troubleshooting: Render autodeploy (GitHub webhook vazio)

Este arquivo descreve um passo-a-passo para resolver quando o webhook do Render não existe ou está vazio e o autodeploy não dispara.

Cenário comum

- Você faz push no GitHub, mas o Render não inicia deploy.
- Em GitHub → Settings → Webhooks o painel está vazio (não existe webhook do Render).

Solução recomendada (reconectar via Render UI)

1) Verificar Auto-Deploy e Source

- Acesse: https://dashboard.render.com/ → seu serviço (ex: fastapi-sandbox)
- Vá em Settings → Build & Deploy / Source
- Confirme se o repositório está conectado (`wmiltecti/fastapi_sandbox`) e a branch correta (ex: `master`)
- Habilite `Auto-Deploy` se estiver desativado

2) Reconectar o repositório (recomendado)

- Se o webhook estiver ausente, desconecte e reconecte o repositório:
  - Em Render → Service → Settings → Source clique em `Disconnect` (se já estiver conectado)
  - Clique em `Connect Repository`
  - Escolha `wmiltecti/fastapi_sandbox` e autorize o acesso ao GitHub
  - Selecione a branch `master` e habilite `Auto-Deploy`

- A reconexão faz com que o Render crie automaticamente o webhook correto no GitHub.

3) Verificar Webhooks no GitHub

- GitHub → repositório → Settings → Webhooks
- Deve existir um webhook do Render com status `Active`.
- Clique no webhook e veja `Recent Deliveries` para inspecionar payloads e respostas.

4) Testar autodeploy (commit vazio)

No Windows PowerShell local, rode:

```powershell
git commit --allow-empty -m "ci: trigger redeploy test"; git push
```

- Após o push, verifique em Render → Deploys se um novo deploy foi iniciado.

5) Se prefere não reconectar (opção avançada)

- É possível criar um webhook manualmente no GitHub, porém precisa da URL do endpoint do Render (ex: `https://api.render.com/deploy/....`) — essa URL é gerada pelo Render e varia por serviço, por isso a reconexão via UI é recomendada.

6) Se o webhook existe mas o deploy falha

- Em GitHub → Webhooks → selecione a delivery com erro e copie o `Response` e o HTTP status
- Em Render → Service → Deploys → abra o build falho e copie as linhas relevantes do `Build logs`
- Cole aqui os trechos (50–200 linhas em torno do erro) e eu analiso

7) Verificação extra: GitHub App e permissions

- Verifique em https://github.com/settings/installations se o GitHub App do Render está instalado e com permissões para o repositório
- Se a instalação foi revogada, reautorize o Render a acessar seu repositório

Próximos passos sugeridos

- Se quiser, posso:
  - orientar você durante a reconexão no Render (por chamada ou passo a passo)
  - analisar as deliveries/logs caso você cole-as aqui
  - adicionar um pequeño script de teste de deploy se preferir automatizar verificações


Document created automatically to help resolve webhook/autodeploy issues.
