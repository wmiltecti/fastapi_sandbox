import os, re, json, time, base64, logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
import psycopg2
import psycopg2.extras
from psycopg_pool import ConnectionPool
import hashlib, base64
import os
import psycopg2.extras

# importe bcrypt no topo do arquivo (já sugerido antes)
try:
    import bcrypt
except Exception:
    bcrypt = None

from typing import Optional

def verify_and_maybe_migrate_password(user_id: int, input_password: str, stored_password: Optional[str]) -> bool:
    """
    Ordem de verificação:
      1) bcrypt ($2a/$2b/$2y)
      2) md5 (32 hex)
      3) sha1-base64 (20 bytes em base64 -> ~28 chars)
      4) texto claro (fallback)
    """
    if not stored_password:
        return False

    sp = stored_password.strip()

    # 1) bcrypt
    if (bcrypt is not None) and (sp.startswith("$2a$") or sp.startswith("$2b$") or sp.startswith("$2y$")):
        try:
            return bcrypt.checkpw(input_password.encode("utf-8"), sp.encode("utf-8"))
        except Exception:
            return False

    # 2) MD5 (32 hex)
    if len(sp) == 32 and all(c in "0123456789abcdefABCDEF" for c in sp):
        md5hex = hashlib.md5(input_password.encode("utf-8")).hexdigest()
        if md5hex.lower() == sp.lower():
            # (opcional) migrar para bcrypt
            # _migrate_to_bcrypt(user_id, input_password)
            return True
        return False

    # 3) SHA-1 base64 (20 bytes → base64 ~28 chars, termina com '=')
    #    Ex.: 'Urorqwrz+lsu8sExenn5dfjwBUs='
    try:
        # tenta decodificar base64 e ver se tem 20 bytes
        raw = base64.b64decode(sp, validate=True)
        if len(raw) == 20:
            sha1_b64 = base64.b64encode(hashlib.sha1(input_password.encode("utf-8")).digest()).decode()
            if sha1_b64 == sp:
                # (opcional) migrar para bcrypt
                # _migrate_to_bcrypt(user_id, input_password)
                return True
    except Exception:
        pass  # não é base64 válido → segue

    # 4) texto claro (fallback de compatibilidade)
    return sp == input_password

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

class UserResponse(BaseModel):
    """Response model para representar um usuário na listagem."""
    id: int
    nome: str
    login: str
    active: bool = True
    bloqueado: bool = False

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

SQL_LIST_USERS = f"""
SELECT
  u.pk_x_usr AS id,
  u.name AS nome,
  u.login,
  COALESCE(u.active, 1) AS active,
  COALESCE(u.bloqueado, 0) AS bloqueado
FROM {PGSCHEMA}.x_usr u
ORDER BY u.name;
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


@app.get("/db-check", tags=["infra"])
def db_check():
    """Pequeno healthcheck que valida a conexão com o banco (SELECT 1).
    Útil para testar se as variáveis de ambiente e a rede estão corretas no Render.
    """
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            row = cur.fetchone()
            cur.close()
        ok = bool(row and row[0] == 1)
        return {"db": "ok" if ok else "unexpected result", "result": row}
    except Exception as e:
        logger.exception("DB check failed")
        raise HTTPException(status_code=500, detail={"message": "DB connection failed", "error": str(e)}) from e
@app.get("/users", response_model=list[UserResponse], tags=["users"], summary="Listar usuários")
def list_users():
    """Lista todos os usuários cadastrados no sistema.
    Retorna informações básicas como id, nome, login e status.
    """
    try:
        with pool.connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(SQL_LIST_USERS)
            users = [dict(row) for row in cur.fetchall()]
            cur.close()
            return users
    except Exception as e:
        logger.exception("Failed to list users")
        raise HTTPException(
            status_code=500,
            detail={"message": "Erro ao listar usuários", "error": str(e)}
        ) from e

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
        with pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(SQL_AUTH_X_USR, {"login_digits": login_digits})
            row = cur.fetchone()
            if row:
                u = dict(zip([desc[0] for desc in cur.description], row))
            else:
                u = None
            cur.close()
    except Exception as e:
        logger.exception("Erro ao consultar x_usr")
        raise HTTPException(status_code=500, detail={"message": "Erro interno de banco."}) from e

    if not u:
        raise HTTPException(status_code=401, detail={"message": "Credenciais inválidas."})
    if int(u["active"]) == 0 or int(u.get("bloqueado", 0)) == 1:
        raise HTTPException(status_code=403, detail={"message": "Usuário inativo/bloqueado."})
    stored_pw = u.get("user_password")
    if not verify_and_maybe_migrate_password(int(u["user_id"]), body.senha, stored_pw):
        raise HTTPException(status_code=401, detail={"message": "Credenciais inválidas."})


    user_id = int(u["user_id"])

    # --- nome para exibição em f_pessoa
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(SQL_PERSON_NAME, {"user_id": user_id})
            row = cur.fetchone()
            if row:
                p = dict(zip([desc[0] for desc in cur.description], row))
            else:
                p = None
            cur.close()
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
