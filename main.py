import os, base64, json, time, re
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import psycopg
from psycopg_pool import ConnectionPool

from dotenv import load_dotenv, find_dotenv
load_dotenv(dotenv_path=find_dotenv(), override=True)

try:
    import bcrypt
except Exception:
    bcrypt = None

APP_TITLE = "Licenciamento Ambiental – Auth (Supabase)"
APP_VERSION = "2.1.0"
APP_DESCRIPTION = """
API de autenticação usando **public.f_pessoa** no Postgres (Supabase).  
Use **/auth/login** para validar credenciais.  
Ambiente de teste: configure variáveis PGHOST/PGDATABASE/PGUSER/PGPASSWORD/PGPORT/PGSCHEMA.

**Atalhos:**
- Swagger UI: **`/docs`**
- ReDoc: **`/redoc`**
"""

tags_metadata = [
    {"name": "health", "description": "Verificação de disponibilidade do serviço."},
    {"name": "auth", "description": "Fluxos de autenticação baseados em `f_pessoa`."},
]

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste conforme necessidade
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- MODELOS ----------
class ErrorResponse(BaseModel):
    message: str = Field(..., examples=["Credenciais inválidas."])

class LoginBody(BaseModel):
    login: str = Field(..., examples=["123.456.789-00", "11.222.333/0001-44", "PASS1234"])
    senha: str = Field(..., examples=["minhasenha"])
    tipoDeIdentificacao: Optional[str] = Field(
        None, examples=["CPF", "CNPJ", "PASSAPORTE", "ESTRANGEIRO"]
    )

class LoginResponse(BaseModel):
    token: str = Field(..., description="Token mock (base64).")
    nome: Optional[str] = Field(None, examples=["Fulano de Tal"])
    perfil: Optional[str] = Field(None, examples=["ADMIN"])
    userId: str = Field(..., examples=["1"])

# --------- HELPERS ----------
def norm(s: str) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", (s or "")).upper()

def issue_mock_token(payload: dict) -> str:
    payload = dict(payload)
    payload["iat"] = int(time.time())
    raw = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

# --------- ENV / PARAMS ----------
PGHOST=os.getenv("PGHOST")
PGDATABASE=os.getenv("PGDATABASE", "postgres")
PGUSER=os.getenv("PGUSER", "postgres")
PGPASSWORD=os.getenv("PGPASSWORD")
PGPORT=int(os.getenv("PGPORT", "5432"))
PGSCHEMA=os.getenv("PGSCHEMA", "public")
PERSON_TABLE=os.getenv("PERSON_TABLE", "f_pessoa")

COL_ID=os.getenv("PERSON_COL_ID", "id")
COL_NOME=os.getenv("PERSON_COL_NOME", "nome")
COL_PERFIL=os.getenv("PERSON_COL_PERFIL", "perfil")
COL_TIPO=os.getenv("PERSON_COL_TIPO", "tipo")
COL_CPF=os.getenv("PERSON_COL_CPF", "cpf")
COL_CNPJ=os.getenv("PERSON_COL_CNPJ", "cnpj")
COL_PASSAPORTE=os.getenv("PERSON_COL_PASSAPORTE", "passaporte")
COL_ESTRANGEIRO=os.getenv("PERSON_COL_ESTRANGEIRO", "identificacao_estrangeiro")
COL_SENHA=os.getenv("PERSON_COL_SENHA", "senha")
COL_SENHA_HASH=os.getenv("PERSON_COL_SENHA_HASH", "senha_hash")

if not (PGHOST and PGPASSWORD):
    raise RuntimeError("Defina PGHOST e PGPASSWORD no ambiente.")
os.environ.setdefault("PGSSLMODE", "require")  # Supabase precisa SSL

DB_DSN = (
    f"host={PGHOST} port={PGPORT} dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD} sslmode={os.getenv('PGSSLMODE')}"
)

pool = ConnectionPool(
    conninfo=DB_DSN,
    min_size=1,
    max_size=10,
    kwargs={"autocommit": True}
)

# --------- QUERIES ----------
SQL_FIND_USER = f"""
SELECT
  {COL_ID} AS id,
  {COL_NOME} AS nome,
  {COL_PERFIL} AS perfil,
  {COL_TIPO} AS tipo,
  {COL_CPF} AS cpf,
  {COL_CNPJ} AS cnpj,
  {COL_PASSAPORTE} AS passaporte,
  {COL_ESTRANGEIRO} AS identificacao_estrangeiro,
  {COL_SENHA} AS senha,
  {COL_SENHA_HASH} AS senha_hash
FROM {PGSCHEMA}.{PERSON_TABLE}
WHERE
  regexp_replace(upper(coalesce({COL_CPF}, '')), '[^0-9A-Z]', '', 'g') = %(nlogin)s
  OR regexp_replace(upper(coalesce({COL_CNPJ}, '')), '[^0-9A-Z]', '', 'g') = %(nlogin)s
  OR regexp_replace(upper(coalesce({COL_PASSAPORTE}, '')), '[^0-9A-Z]', '', 'g') = %(nlogin)s
  OR regexp_replace(upper(coalesce({COL_ESTRANGEIRO}, '')), '[^0-9A-Z]', '', 'g') = %(nlogin)s
LIMIT 1;
"""

def find_user_in_db(login: str):
    nlogin = norm(login)
    with pool.connection() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(SQL_FIND_USER, {"nlogin": nlogin})
            return cur.fetchone()

def verify_password(input_password: str, row: dict) -> bool:
    hash_from_db = row.get("senha_hash")
    plain_from_db = row.get("senha")

    if hash_from_db:
        if not bcrypt:
            return False
        try:
            return bcrypt.checkpw(input_password.encode("utf-8"), hash_from_db.encode("utf-8"))
        except Exception:
            return False
    return (plain_from_db or "") == input_password

# --------- ENDPOINTS ----------
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "supabase-api", "version": APP_VERSION}

@app.post(
    "/auth/login",
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Requisição inválida"},
        401: {"model": ErrorResponse, "description": "Credenciais inválidas"},
    },
    tags=["auth"],
    summary="Autenticar usuário pelo documento",
    description="""
Tenta autenticar por **CPF**, **CNPJ**, **PASSAPORTE** ou **Identificação de Estrangeiro** (o que casar primeiro).  
Senha pode ser validada por **hash Bcrypt** (`senha_hash`) ou **texto claro** (`senha`).
""",
)
def login(body: LoginBody):
    row = find_user_in_db(body.login)
    if not row:
        raise HTTPException(status_code=401, detail={"message": "Credenciais inválidas."})

    if not verify_password(body.senha, row):
        raise HTTPException(status_code=401, detail={"message": "Credenciais inválidas."})

    tipo = (row.get("tipo") or "").upper()
    if tipo == "ESTRANGEIRO":
        if body.tipoDeIdentificacao not in {"CNPJ", "CPF", "PASSAPORTE", "ESTRANGEIRO"}:
            raise HTTPException(status_code=400, detail={"message": "tipoDeIdentificacao obrigatório para estrangeiro."})
        token = issue_mock_token({"sub": str(row.get("id") or body.login), "tipo": tipo, "tdi": body.tipoDeIdentificacao})
    else:
        token = issue_mock_token({"sub": str(row.get("id") or body.login), "tipo": tipo})

    return {
        "token": token,
        "nome": row.get("nome"),
        "perfil": row.get("perfil"),
        "userId": str(row.get("id") or body.login)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main_supabase:app", host="0.0.0.0", port=port, reload=False)
