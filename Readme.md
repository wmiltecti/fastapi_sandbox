Aqui está o **README.md** prontinho para o seu projeto `fastapi_sandbox` — com passos para instalar, ativar o ambiente, configurar `.env` e executar (via `start.sh` ou diretamente com Uvicorn). Ele considera o conteúdo atual de `main.py`, `requirements.txt` e `start.sh`.

---

# fastapi_sandbox

API FastAPI com autenticação via Postgres (Supabase), documentação automática (Swagger UI) e endpoints prontos para teste local.

## Requisitos

* **Python 3.11+** (recomendado)
* **pip** atualizado
* Acesso ao banco (Supabase/Postgres)

## Estrutura básica

* `main.py` – app FastAPI com `/health` e `/auth/login` (inclui Swagger UI e ReDoc). 
* `requirements.txt` – dependências da aplicação. 
* `start.sh` – script simples de inicialização (instala requirements e roda a app). 
* `.env` – variáveis de ambiente (não versionado)

---

## 1) Criar e ativar o ambiente virtual

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS (bash)

```bash
python -m venv .venv
source .venv/bin/activate
```

> Dica: confirme a versão do Python ativo com `python -V`.

---

## 2) Configurar as variáveis de ambiente (.env)

Crie um arquivo `.env` na raiz (ou exporte no shell). Para Supabase/Postgres, **exija SSL**:

```dotenv
# Banco (Supabase)
PGHOST=db.jnhvlqytvssrbwjpolyq.supabase.co
PGDATABASE=postgres
PGUSER=postgres
PGPASSWORD=<<SUA_SENHA_AQUI>>
PGPORT=5432
PGSCHEMA=public
PGSSLMODE=require

# (Opcional) Renomeie colunas, se seu schema diferir
# PERSON_TABLE=f_pessoa
# PERSON_COL_ID=id
# PERSON_COL_NOME=nome
# PERSON_COL_PERFIL=perfil
# PERSON_COL_TIPO=tipo
# PERSON_COL_CPF=cpf
# PERSON_COL_CNPJ=cnpj
# PERSON_COL_PASSAPORTE=passaporte
# PERSON_COL_ESTRANGEIRO=identificacao_estrangeiro
# PERSON_COL_SENHA=senha
# PERSON_COL_SENHA_HASH=senha_hash

# Porta local
PORT=8000
```

> Se você **não** usa `python-dotenv`, exporte as variáveis diretamente no terminal antes de rodar (veja exemplos no passo 4).

---

## 3) Instalar dependências

Com o ambiente virtual **ativo**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

As libs incluem `fastapi`, `uvicorn[standard]`, `python-multipart` (e outras adicionadas no código, como `psycopg` e `psycopg_pool`). 

---

## 4) Executar a aplicação

### Opção A — usar o script `start.sh`

O script já instala os requirements e executa `python main.py` (usa `PORT` se definido). 

#### Linux/macOS

```bash
chmod +x start.sh
./start.sh
```

#### Windows (PowerShell)

```powershell
# simule o script manualmente
pip install -r requirements.txt
$env:PORT="8000"
python .\main.py
```

### Opção B — rodar direto com Uvicorn (recomendado em dev)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> Observação importante: se ao rodar `python main.py` aparecer erro do tipo **“No module named main_supabase”**, execute com Uvicorn como acima (`main:app`) ou ajuste a chamada interna do `uvicorn.run` no arquivo para usar `app` diretamente. O conteúdo de `main.py` habilita Swagger/Redoc e endpoints como descritos aqui. 

---

## 5) Endpoints e documentação

* **Swagger UI**: `http://localhost:8000/docs`
* **ReDoc**: `http://localhost:8000/redoc`

**Healthcheck**

```bash
curl http://localhost:8000/health
```

**Login** (exemplo por CPF; substitua credenciais por dados reais da sua `public.f_pessoa`)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"123.456.789-00","senha":"minhasenha"}'
```

* O Swagger foi configurado com `persistAuthorization=true` no UI. 

---

## 6) Dicas de teste

* **Supabase exige SSL**: mantenha `PGSSLMODE=require` no `.env`.
* Se usar **hash de senha (bcrypt)**, garanta que a coluna `senha_hash` esteja preenchida; caso contrário, o código tenta validar pela coluna `senha` em texto (fallback). 
* Para um teste rápido, insira um usuário temporário na `f_pessoa` com senha em texto (ajuste nomes de colunas se necessário):

  ```sql
  insert into public.f_pessoa
    (id, nome, perfil, tipo, cpf, senha)
  values
    (1, 'Fulano de Tal', 'ADMIN', 'CPF', '12345678900', 'minhasenha');
  ```

---

## 7) Solução de problemas

* **`password authentication failed`** → confira `PGUSER/PGPASSWORD` no Supabase.
* **Timeout/`no pg_hba.conf entry`** → verifique `PGHOST`, `PGPORT` e SSL habilitado (`PGSSLMODE=require`).
* **Erro ao subir com `python main.py`** → rode com `uvicorn main:app --reload` (ou ajuste a linha do `uvicorn.run` no `main.py`). 
* **CORS**: por padrão, o app permite `allow_origins=["*"]`; restrinja conforme necessidade no `main.py`. 

### Conexão com Supabase no Render

Se encontrar problemas de conexão no Render (ex: timeout após 30 segundos), considere usar o Shared Pooler:

```dotenv
# Configuração para Shared Pooler (recomendado para Render/IPv4)
PGHOST=aws-1-sa-east-1.pooler.supabase.com
PGPORT=6543
PGUSER=postgres.[seu-projeto-id]  # ex: postgres.jnhvlqytvssrbwjpolyq
```

Notas importantes:
* O Dedicated Pooler não suporta IPv4 mesmo com o add-on IPv4 ativado
* O Shared Pooler tem suporte nativo a IPv4 e é recomendado para deploy no Render
* Use a porta 6543 para connection pooling (não 5432)
* O usuário deve ter o prefixo `postgres.` seguido do ID do projeto

---

## 8) Execução em outra porta

```bash
# Linux/macOS
export PORT=8080
uvicorn main:app --host 0.0.0.0 --port $PORT --reload
```

```powershell
# Windows
$env:PORT="8080"
uvicorn main:app --host 0.0.0.0 --port $env:PORT --reload
```

Se usar `start.sh`, defina `PORT` antes de executá-lo. 

---

## 9) Próximos passos (opcional)

* Adicionar `Dockerfile`/`docker-compose.yml`
* Testes automatizados (pytest) para `/health` e `/auth/login` (mockando DB)
* Pipeline CI para lint, testes e build

---

Se quiser, eu já te entrego o `Dockerfile` + `docker-compose.yml` e um `Makefile` com alvos `setup / run / test` seguindo este README.

sbp_3909a7292a682192d2d8f714c24c884dc3e560dd
jnhvlqytvssrbwjpolyq
