README: Deploy / Logs (Render)

Este arquivo contém instruções rápidas e reproduzíveis para:

- configurar variáveis de ambiente no Render
- forçar um redeploy e validar a versão do Python
- localizar e copiar os logs de deploy e runtime no dashboard do Render
- coletar logs via CLI (opções) e compartilhar comigo para investigação

IMPORTANTE: este arquivo foi adicionado sem alterar o `Readme.md` principal.

1) Conferir variáveis de ambiente no Render

- Acesse: https://dashboard.render.com/ → seu serviço (ex: fastapi-sandbox)
- Aba: "Environment" ou "Environment Variables"
- Confirme as variáveis obrigatórias (exemplos):
  - PGHOST=db.<seu-projeto>.supabase.co
  - PGDATABASE=postgres
  - PGUSER=postgres
  - PGPASSWORD=(secret)
  - PGPORT=5432
  - PGSCHEMA=public
  - PGSSLMODE=require
- Salve e clique em "Manual Deploy" (ou faça um push) para aplicar.

2) Forçar um redeploy (opções)

- Push no GitHub (gera redeploy automático):

  git commit --allow-empty -m "Trigger redeploy"; git push

- Ou no dashboard → Deploys → Manual Deploy

3) Validar a versão do Python usada pelo build

- No dashboard de Deploy, abra a execução mais recente e procure por linhas como:
  - "Installing Python version X..."
  - "Using Python version X (default)"

Se a versão não for a desejada (ex.: 3.11.9), altere no dashboard em Settings → Runtime / Python Version e redeploy.

4) Onde encontrar os logs (deploy e runtime)

- Deploy logs: Dashboard → Service → Deploys → clique no deploy em andamento/recente → Build logs
  - Procure por seções: "Installing Python", "Installing dependencies", "Running startup command"
- Live logs / Server logs: Dashboard → Service → Logs (ou "Live logs")
  - Aqui você verá o output do Uvicorn, mensagens de erro (tracebacks) e os warnings da biblioteca.

5) Como coletar e enviar logs para investigação

- Copie do painel as linhas relevantes do Build logs e do Live logs. Se os logs forem longos, copie 50–200 linhas em torno do erro.
- Se preferir, salve em um arquivo e anexe aqui (ou cole o trecho). Exemplo:

  # No seu shell local (após copiar o trecho):
  cat > render-logs.txt
  # cole os logs
  CTRL-D

- Em alternativa, se quiser me dar acesso temporário, gere um "Support session" no Render (se disponível) ou me forneça apenas o trecho de logs que contém a palavra-chave do erro (ex.: "PoolTimeout" ou "Network is unreachable").

6) Coletar logs via CLI (opções)

- Render não possui um cliente oficial universal para logs via terminal sem autenticação. As duas formas mais simples são:
  - Usar o dashboard (web UI) — recomendado
  - Usar a API do Render (requer API key e endpoint específico) — não configurado por padrão

7) Mensagens-chave para procurar nos logs

- "Network is unreachable" → conexão IPv4/IPv6
- "couldn't get a connection after 30.00 sec" / PoolTimeout → problema de conexão ou bloqueio
- "password authentication failed" → credenciais incorretas
- Tracebacks completos (colapsar frames do uvicorn para focar no erro do DB)

8) Teste rápido — endpoint /db-check

- Está disponível: GET /db-check
- Resultado esperado quando DB ok:
  {"db":"ok","result":[1]}
- Se retornar 500, copie o campo "error" do detalhamento da resposta JSON e cole aqui.

9) Próximos passos (posso fazer)

- Se você colar os logs do último deploy/erro, eu analiso e te retorno a causa provável e a ação (config/var/env/Script).
- Posso também criar um script adicional para rodar um teste de conexão remoto (usando sua chave — NÃO envie a chave em claro aqui; use secrets ou execute o script localmente).


Se quiser, eu já faço o commit deste README no repositório (já criado) e posso abrir um PR com uma checklist interativa. Se já tiver os logs, cole-os aqui e eu começo a analisar.
