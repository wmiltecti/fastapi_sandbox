Perfeito — aqui está o `main.py` **completo**, já consolidando tudo que definimos até agora:

✅ Autenticação em `x_usr` (login e senha)
✅ Limpeza de máscara (CPF → só dígitos)
✅ Busca do nome em `f_pessoa` via `fkuser`
✅ Manutenção dos quatro perfis (`CPF`, `CNPJ`, `PASSAPORTE`, `ESTRANGEIRO`) no contrato
✅ Swagger UI (`/docs`) e ReDoc (`/redoc`)
✅ Health check `/health`
✅ Pool de conexões com `psycopg_pool`
✅ Carregamento automático de `.env` (com `python-dotenv`)

---

```python
import os, re, json, time, base64, logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
import psycopg
from psycopg_pool import ConnectionPool

# -------------------------------------------------------
# Inicialização e configuração geral
# -------------------------------------------------------
load_dotenv(find_dotenv(), override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_sandbox")

app = FastAPI(
    title="Licenciamento Ambiental – Auth (Supabase)",
    version="3.0.0",
    description="""
API de autenticação integrada ao Supabase/Postgres.  
Fluxo atual: **CPF** via `x_usr`, com nome em `f_pessoa`.  
Outros perfis (CNPJ, PASSAPORTE, ESTRANGEIRO) já previstos no contrato e liberados evolutivamente.
""",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Conexão ao banco (Supabase/Postgres)
# -------------------------------------------------------
PGHOST = os.getenv("PGHOST")
PGDATABASE = os.getenv("PGDATABASE", "postgres")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD")
PGPORT = int(os.getenv("PGPORT", "5432"))
PGSCHEMA = os.getenv("PGSCHEMA", "public")

os.environ.setdefault("PGSSLMODE", "require")

if not (PGHOST and PGPASSWORD):
    raise RuntimeError("Defina PGHOST e PGPASSWORD no ambiente (.env).")

DSN = f"host={PGHOST} port={PGPORT} dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD} sslmode={os.getenv('PGSSLMODE','require')}"

pool = ConnectionPool(conninfo=DSN, min_size=1, max_size=10, kwargs={"autocommit": True})

# -------------------------------------------------------
# Modelos de dados (Swagger)
# -------------------------------------------------------
TIPOS_VALIDOS = {"CPF", "CNPJ", "PASSAPORTE", "ESTRANGEIRO"}

class LoginBody(BaseModel):
    login: str = Field(..., description="Documento informado no login")
    senha: str = Field(..., description="Senha do usuário")
    tipoDeIdentificacao: Optional[str] = Field(
        None,
        description="CPF | CNPJ | PASSAPORTE | ESTRANGEIRO",
        examples=["CPF", "CNPJ", "PASSAPORTE", "ESTRANGEIRO"],
    )

class LoginResponse(BaseModel):
    token: str
    nome: str
    userId: str

# -------------------------------------------------------
# SQLs principais
# -------------------------------------------------------
SQL_AUTH_X_USR = f"""
SELECT
  u.pk_x_usr AS user_id,
  u.name     AS user_name,
  u.login    AS user_login,
  u.password AS user_password,
  COALESCE(u.active,1)    AS active,
  COALESCE(u.bloqueado,0) AS bloqueado
FROM {PGSCHEMA}.x_usr u
WHERE regexp_replace(u.login, '\\D', '', 'g') = %(login_digits)s
LIMIT 1;
"""

SQL_PERSON_NAME = f"""
SELECT
  p.fkuser,
  COALESCE(NULLIF(p.nomepessoa,''), NULLIF(p.nome,''), NULLIF(p.nomerazao,''), NULLIF(p.razaosocial,'')) AS display_name
FROM {PGSCHEMA}.f_pessoa p
WHERE p.fkuser = %(user_id)s
LIMIT 1;
"""

# -------------------------------------------------------
# Funções auxiliares
# -------------------------------------------------------
def only_digits(s: str) -> str:
    return re.sub(r"\D+", "", (s or ""))

def issue_token(payload: dict) -> str:
    payload = dict(payload)
    payload["iat"] = int(time.time())
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")

# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------
@app.get("/health", tags=["infra"])
def health():
    """Verificação de disponibilidade básica."""
    return {"status": "ok", "service": "fastapi_sandbox", "version": "3.0.0"}

@app.post("/auth/login", response_model=LoginResponse, tags=["auth"], summary="Autenticar usuário (CPF)")
def login(body: LoginBody):
    """Autentica usuário no Supabase:
    - Usa x_usr (login, password)
    - Busca nome em f_pessoa.fkuser
    - Tipos previstos: CPF, CNPJ, PASSAPORTE, ESTRANGEIRO (escopo atual: CPF)
    """
    tipo = (body.tipoDeIdentificacao or "CPF").upper()
    if tipo not in TIPOS_VALIDOS:
        raise HTTPException(status_code=400, detail={"message": "tipoDeIdentificacao inválido."})

    if tipo != "CPF":
        raise HTTPException(status_code=422, detail={"message": f"Autenticação por {tipo} será habilitada nas próximas etapas."})

    # --- normaliza login
    login_digits = only_digits(body.login)
    if not login_digits:
        raise HTTPException(status_code=400, detail={"message": "Informe um CPF válido."})

    # --- autenticação em x_usr
    try:
        with pool.connection() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(SQL_AUTH_X_USR, {"login_digits": login_digits})
            u = cur.fetchone()
    except Exception as e:
        logger.exception("Erro ao consultar x_usr")
        raise HTTPException(status_code=500, detail={"message": "Erro interno de banco."}) from e

    if not u:
        raise HTTPException(status_code=401, detail={"message": "Credenciais inválidas."})
    if int(u["active"]) == 0 or int(u.get("bloqueado", 0)) == 1:
        raise HTTPException(status_code=403, detail={"message": "Usuário inativo/bloqueado."})
    if (u["user_password"] or "") != body.senha:
        raise HTTPException(status_code=401, detail={"message": "Credenciais inválidas."})

    user_id = int(u["user_id"])

    # --- nome para exibição em f_pessoa
    try:
        with pool.connection() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(SQL_PERSON_NAME, {"user_id": user_id})
            p = cur.fetchone()
    except Exception as e:
        logger.exception("Erro ao buscar nome em f_pessoa")
        raise HTTPException(status_code=500, detail={"message": "Erro interno de banco."}) from e

    display_name = (p or {}).get("display_name") or (u["user_name"] or u["user_login"])

    token = issue_token({"sub": str(user_id), "tipo": tipo})

    return {
        "token": token,
        "nome": display_name,
        "userId": str(user_id)
    }

# -------------------------------------------------------
# Execução local
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
```

---

## 🔍 Fluxo resumido

1. **Login CPF:**

   * O usuário digita o CPF (com ou sem máscara).
   * O código limpa (`\D`) e procura em `x_usr.login`.
   * Se `password` confere → autentica.

2. **Busca nome:**

   * Consulta `f_pessoa.fkuser = x_usr.pk_x_usr`.
   * Exibe `nomepessoa` ou similar na resposta.

3. **Outros tipos (CNPJ, PASSAPORTE, ESTRANGEIRO):**

   * Mantidos no contrato (para o front não quebrar).
   * Retornam `422` com mensagem:
     `"Autenticação por <tipo> será habilitada nas próximas etapas."`

---

✅ **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
✅ **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
✅ **Health check:** [http://localhost:8000/health](http://localhost:8000/health)

---

Deseja que eu adicione agora:

* ✅ **/auth/me** (retorna info do usuário a partir do token emitido), e
* ✅ **estrutura de perfis/roles** (`x_grp` / `fk_x_grp`) para já preparar o JWT com permissões?


exemplo de conmexao no supabase com pyhton
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")