import os, re, json, time, base64, logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
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
import httpx

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

# Importar configurações e router v1
from app.config import settings
from app.routers.api_v1_processos import router as v1_processos_router
from app.middleware.request_id import RequestIDMiddleware

# Criar router para rotas legadas (auth, pessoas, car, blockchain, users)
from fastapi import APIRouter
legacy_router = APIRouter()

# Tags metadata para organização do Swagger
tags_metadata = [
    {
        "name": "v1-processos",
        "description": """
        **API v1** - Gerenciamento de processos de licenciamento ambiental.
        
        Utiliza Supabase REST API com autenticação JWT e RLS (Row Level Security).
        
        Workflow típico:
        1. **POST /api/v1/processos** - Criar processo
        2. **PUT /api/v1/processos/{id}/dados-gerais** - Cadastrar dados gerais
        3. **POST /api/v1/processos/{id}/localizacoes** - Adicionar localizações
        4. **GET /api/v1/processos/{id}/wizard-status** - Verificar status
        5. **POST /api/v1/processos/{id}/submit** - Submeter para revisão
        """,
    },
    {
        "name": "Auth",
        "description": "Endpoints de autenticação e login (legacy)",
    },
    {
        "name": "Pessoas",
        "description": "Consulta de pessoas físicas e jurídicas (legacy)",
    },
    {
        "name": "CAR",
        "description": "Consulta de imóveis CAR (legacy)",
    },
    {
        "name": "Blockchain",
        "description": "Integração com Continuus Blockchain para registro de processos",
    },
]

# Servidores para documentação
servers = [
    {
        "url": "http://localhost:8000",
        "description": "Ambiente de desenvolvimento local"
    },
    {
        "url": "https://fastapi-sandbox.onrender.com",
        "description": "Ambiente de produção (Render)"
    }
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
API de autenticação integrada ao Supabase/Postgres.  
Fluxo atual: **CPF** via `x_usr`, com nome em `f_pessoa`.  
Outros perfis (CNPJ, PASSAPORTE, ESTRANGEIRO) já previstos no contrato e liberados evolutivamente.

**API v1** disponível em `/api/v1` com integração Supabase REST.
Todos os endpoints v1 requerem autenticação via **Bearer Token JWT**.
""",
    swagger_ui_parameters={"persistAuthorization": True},
    openapi_tags=tags_metadata,
    servers=servers,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Permite qualquer origem (desenvolvimento e produção)
    allow_credentials=False,        # IMPORTANTE: deve ser False quando allow_origins=["*"]
    allow_methods=["*"],            # ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    allow_headers=["*"],            # precisa incluir "Authorization" se você enviar Bearer
)
# Security scheme para JWT Bearer
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
        servers=servers,
    )
    
    # Adicionar HTTPBearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT do usuário do Supabase. Obtenha via login ou geração de token."
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Middleware Request-ID
app.add_middleware(RequestIDMiddleware)

# CORS com configuração do settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CORS (único) ---
from fastapi.middleware.cors import CORSMiddleware
import os

IS_DEV = os.getenv("ENV", "dev").lower() in ("dev", "development", "local")

if IS_DEV:
    # Em desenvolvimento: liberar geral (sem credenciais)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],       # ok pq não usaremos credenciais
        allow_credentials=False,   # IMPORTANTÍSSIMO p/ permitir "*"
        allow_methods=["*"],
        allow_headers=["*"],       # inclui Authorization
    )
else:
    # Produção/Homolog: orígens explícitas (edite settings.CORS_ORIGINS)
    # Ex.: settings.CORS_ORIGINS = ["https://seu-front.com", "https://homolog.seu-front.com"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS or [],
        allow_credentials=True,    # se precisar enviar cookies
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Montar router v1 com prefix configurável
app.include_router(v1_processos_router, prefix=settings.API_BASE)

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
    """Response model para representar um usuário."""
    id: int = Field(..., alias='pk_x_usr')
    name: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = True
    fk_x_grp: Optional[int] = None
    description: Optional[str] = None
    administrator: Optional[bool] = None
    email: Optional[str] = None
    fk_x_mod: Optional[int] = None
    changepassword: Optional[bool] = None
    bloqueado: Optional[bool] = None
    administradoraplicativofiscalizacao: Optional[bool] = None

class ImovelResponse(BaseModel):
    """Response model para representar um imóvel."""
    id: int = Field(..., alias='pkimovel')
    nome: Optional[str] = None
    areatotal: Optional[float] = None
    numero: Optional[str] = None
    livro: Optional[str] = None
    folha: Optional[str] = None
    cartorio: Optional[str] = None
    tipo: Optional[int] = None
    fkmunicipio: Optional[int] = None
    nirf: Optional[str] = None
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    fkpais: Optional[int] = None
    fkestado: Optional[int] = None
    inscricaoMunicipal: Optional[str] = None
    ccirincra: Optional[str] = None
    roteiroAcesso: Optional[str] = None
    cep: Optional[str] = None
    complemento: Optional[str] = None
    endereco: Optional[str] = None
    areaReservaLegal: Optional[float] = None
    areaPreservacaoPermanente: Optional[float] = None
    possuiCar: Optional[bool] = None

class CarResponse(BaseModel):
    """Response model para representar um CAR."""
    id: int = Field(..., alias='pkcar')
    fkimovel: int
    numerocar: str
    situacaocar: Optional[str] = None
    pessoacadastrantedocumento: Optional[str] = None
    pessoacadastrantenome: Optional[str] = None
    datainscricao: Optional[date] = None
    situacaopagamento: Optional[str] = None
    etapaatual: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PessoaResponse(BaseModel):
    """Response model para representar uma pessoa."""
    id: int = Field(..., alias='pkpessoa')
    fkuser: Optional[int] = None
    tipo: Optional[int] = None
    status: Optional[int] = None
    cpf: Optional[str] = None
    nome: Optional[str] = None
    datanascimento: Optional[datetime] = None
    naturalidade: Optional[str] = None
    nacionalidade: Optional[str] = None
    estadocivil: Optional[int] = None
    sexo: Optional[int] = None
    rg: Optional[str] = None
    orgaoemissor: Optional[str] = None
    fkestadoemissor: Optional[int] = None
    fkprofissao: Optional[int] = None
    passaporte: Optional[str] = None
    datapassaporte: Optional[datetime] = None
    cnpj: Optional[str] = None
    razaosocial: Optional[str] = None
    nomefantasia: Optional[str] = None
    inscricaoestadual: Optional[str] = None
    fkufinscricaoestadual: Optional[int] = None
    datainicioatividade: Optional[datetime] = None
    inscricaomunicipal: Optional[str] = None
    cnaefiscal: Optional[str] = None
    simplesnacional: Optional[int] = None
    crccontador: Optional[str] = None
    fknaturezajuridica: Optional[int] = None
    fkporte: Optional[int] = None
    identificacaoestrangeira: Optional[str] = None
    tipoidentificacaoestrangeira: Optional[str] = None
    telefone: Optional[str] = None
    telefonealternativo1: Optional[str] = None
    telefonealternativo2: Optional[str] = None
    email: Optional[str] = None
    emailalternativo: Optional[str] = None
    fax: Optional[str] = None
    faxalternativo: Optional[str] = None
    complemento: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    fkmunicipio: Optional[int] = None
    fkestado: Optional[int] = None
    fkpais: Optional[int] = None
    statusregimeespecial: Optional[int] = None
    dataregimeespecial: Optional[datetime] = None
    periodoregimeespecial: Optional[int] = None
    periodopagamentoregimeespecial: Optional[int] = None
    fkcentroinformacao: Optional[int] = None
    datacadastro: Optional[datetime] = None
    dtype: Optional[int] = None
    numeroconselhoprofissional: Optional[str] = None
    fkconselhoprofissional: Optional[int] = None
    fkestadoemissorconselhoprofissional: Optional[int] = None
    caixapostal: Optional[str] = None
    endereco: Optional[str] = None
    profissao: Optional[str] = None
    situacaopessoajuridica: Optional[int] = None
    porteempresa: Optional[int] = None
    filiacaomae: Optional[str] = None
    filiacaopai: Optional[str] = None
    conjuge_id: Optional[int] = None
    matricula: Optional[str] = None
    nomepessoa: Optional[str] = None
    numeroidentificacao: Optional[str] = None
    nomerazao: Optional[str] = None
    permitirvercarscadastrante: Optional[int] = None
    cargo: Optional[str] = None
    dataultimaalteracao: Optional[datetime] = None
    permitirvercarrt: Optional[int] = None

# -------------------------------------------------------
# Modelos de Blockchain
# -------------------------------------------------------
class BlockchainField(BaseModel):
    """Campo customizado para o blockchain."""
    NmField: str = Field(..., description="Nome do campo")
    DsValue: str = Field(..., description="Descrição/valor do campo")

class BlockchainRegisterRequest(BaseModel):
    """Request model para registrar dados no blockchain."""
    IdBlockchain: int = Field(..., description="ID do registro no blockchain")
    Data: Dict[str, Any] = Field(..., description="Dados a serem registrados")
    Fields: List[BlockchainField] = Field(..., description="Campos customizados")

    class Config:
        json_schema_extra = {
            "example": {
                "IdBlockchain": 1,
                "Data": {
                    "pkpessoa": "2001327",
                    "fkuser": "264637",
                    "cpf": "859.965.722-49",
                    "nome": "ABIMAEL RIBEIRO DE SOUZA"
                },
                "Fields": [
                    {
                        "NmField": "LicenciamentoAmbientalPessoaFisica",
                        "DsValue": "Pessoa fisica do licenciamento ambiental"
                    }
                ]
            }
        }

class BlockchainRegisterResponse(BaseModel):
    """Response model do registro blockchain."""
    success: bool
    message: str
    blockchain_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

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

SQL_LIST_IMOVEIS = f"""
SELECT
  pkimovel,
  nome,
  areatotal,
  numero,
  livro,
  folha,
  cartorio,
  tipo,
  fkmunicipio,
  nirf,
  cidade,
  provincia,
  fkpais,
  fkestado,
  inscricaoMunicipal,
  ccirincra,
  roteiroAcesso,
  cep,
  complemento,
  endereco,
  areaReservaLegal,
  areaPreservacaoPermanente,
  possuiCar
FROM {PGSCHEMA}.f_imovel
ORDER BY nome;
"""

SQL_LIST_CAR = f"""
SELECT
  pkcar,
  fkimovel,
  numerocar,
  situacaocar,
  pessoacadastrantedocumento,
  pessoacadastrantenome,
  datainscricao,
  situacaopagamento,
  etapaatual,
  created_at,
  updated_at
FROM {PGSCHEMA}.f_car
ORDER BY pkcar;
"""

SQL_LIST_USERS = f"""
SELECT
  pk_x_usr,
  name,
  login,
  password,
  COALESCE(active, 1)::boolean as active,
  fk_x_grp,
  description,
  COALESCE(administrator, 0)::boolean as administrator,
  email,
  fk_x_mod,
  COALESCE(changepassword, 0)::boolean as changepassword,
  COALESCE(bloqueado, 0)::boolean as bloqueado,
  COALESCE(administradoraplicativofiscalizacao, 0)::boolean as administradoraplicativofiscalizacao
FROM {PGSCHEMA}.x_usr
ORDER BY name;
"""

SQL_LIST_PESSOAS = f"""
SELECT
  pkpessoa,
  fkuser,
  tipo,
  status,
  cpf,
  nome,
  datanascimento,
  naturalidade,
  nacionalidade,
  estadocivil,
  sexo,
  rg,
  orgaoemissor,
  fkestadoemissor,
  fkprofissao,
  passaporte,
  datapassaporte,
  cnpj,
  razaosocial,
  nomefantasia,
  inscricaoestadual,
  fkufinscricaoestadual,
  datainicioatividade,
  inscricaomunicipal,
  cnaefiscal,
  simplesnacional,
  crccontador,
  fknaturezajuridica,
  fkporte,
  identificacaoestrangeira,
  tipoidentificacaoestrangeira,
  telefone,
  telefonealternativo1,
  telefonealternativo2,
  email,
  emailalternativo,
  fax,
  faxalternativo,
  complemento,
  cep,
  cidade,
  provincia,
  fkmunicipio,
  fkestado,
  fkpais,
  statusregimeespecial,
  dataregimeespecial,
  periodoregimeespecial,
  periodopagamentoregimeespecial,
  fkcentroinformacao,
  datacadastro,
  dtype,
  numeroconselhoprofissional,
  fkconselhoprofissional,
  fkestadoemissorconselhoprofissional,
  caixapostal,
  endereco,
  profissao,
  situacaopessoajuridica,
  porteempresa,
  filiacaomae,
  filiacaopai,
  conjuge_id,
  matricula,
  nomepessoa,
  numeroidentificacao,
  nomerazao,
  permitirvercarscadastrante,
  cargo,
  dataultimaalteracao,
  permitirvercarrt
FROM {PGSCHEMA}.f_pessoa
WHERE cpf IS NOT NULL
AND cpf != ''
ORDER BY COALESCE(NULLIF(nomepessoa,''), NULLIF(nome,''), NULLIF(nomerazao,''), NULLIF(razaosocial,''));
"""

SQL_GET_PESSOA_BY_CPF = f"""
SELECT
  pkpessoa,
  fkuser,
  tipo,
  status,
  cpf,
  nome,
  datanascimento,
  naturalidade,
  nacionalidade,
  estadocivil,
  sexo,
  rg,
  orgaoemissor,
  fkestadoemissor,
  fkprofissao,
  passaporte,
  datapassaporte,
  cnpj,
  razaosocial,
  nomefantasia,
  inscricaoestadual,
  fkufinscricaoestadual,
  datainicioatividade,
  inscricaomunicipal,
  cnaefiscal,
  simplesnacional,
  crccontador,
  fknaturezajuridica,
  fkporte,
  identificacaoestrangeira,
  tipoidentificacaoestrangeira,
  telefone,
  telefonealternativo1,
  telefonealternativo2,
  email,
  emailalternativo,
  fax,
  faxalternativo,
  complemento,
  cep,
  cidade,
  provincia,
  fkmunicipio,
  fkestado,
  fkpais,
  statusregimeespecial,
  dataregimeespecial,
  periodoregimeespecial,
  periodopagamentoregimeespecial,
  fkcentroinformacao,
  datacadastro,
  dtype,
  numeroconselhoprofissional,
  fkconselhoprofissional,
  fkestadoemissorconselhoprofissional,
  caixapostal,
  endereco,
  profissao,
  situacaopessoajuridica,
  porteempresa,
  filiacaomae,
  filiacaopai,
  conjuge_id,
  matricula,
  nomepessoa,
  numeroidentificacao,
  nomerazao,
  permitirvercarscadastrante,
  cargo,
  dataultimaalteracao,
  permitirvercarrt
FROM {PGSCHEMA}.f_pessoa
WHERE regexp_replace(cpf, '\\D', '', 'g') = %(cpf_digits)s
LIMIT 1;
"""

SQL_GET_PESSOA_BY_CNPJ = f"""
SELECT
  pkpessoa,
  fkuser,
  tipo,
  status,
  cpf,
  nome,
  datanascimento,
  naturalidade,
  nacionalidade,
  estadocivil,
  sexo,
  rg,
  orgaoemissor,
  fkestadoemissor,
  fkprofissao,
  passaporte,
  datapassaporte,
  cnpj,
  razaosocial,
  nomefantasia,
  inscricaoestadual,
  fkufinscricaoestadual,
  datainicioatividade,
  inscricaomunicipal,
  cnaefiscal,
  simplesnacional,
  crccontador,
  fknaturezajuridica,
  fkporte,
  identificacaoestrangeira,
  tipoidentificacaoestrangeira,
  telefone,
  telefonealternativo1,
  telefonealternativo2,
  email,
  emailalternativo,
  fax,
  faxalternativo,
  complemento,
  cep,
  cidade,
  provincia,
  fkmunicipio,
  fkestado,
  fkpais,
  statusregimeespecial,
  dataregimeespecial,
  periodoregimeespecial,
  periodopagamentoregimeespecial,
  fkcentroinformacao,
  datacadastro,
  dtype,
  numeroconselhoprofissional,
  fkconselhoprofissional,
  fkestadoemissorconselhoprofissional,
  caixapostal,
  endereco,
  profissao,
  situacaopessoajuridica,
  porteempresa,
  filiacaomae,
  filiacaopai,
  conjuge_id,
  matricula,
  nomepessoa,
  numeroidentificacao,
  nomerazao,
  permitirvercarscadastrante,
  cargo,
  dataultimaalteracao,
  permitirvercarrt
FROM {PGSCHEMA}.f_pessoa
WHERE regexp_replace(cnpj, '\\D', '', 'g') = %(cnpj_digits)s
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
@app.get("/", tags=["infra"], summary="Root endpoint")
def root():
    """Endpoint raiz que retorna informações básicas da API."""
    return {
        "service": "fastapi_sandbox",
        "version": "3.0.0",
        "status": "ok",
        "docs_url": "/docs",
        "health_check": "/health"
    }

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

@legacy_router.get("/users", response_model=list[UserResponse], tags=["users"], summary="Listar usuários")
def list_users():
    """Lista todos os usuários cadastrados no sistema.
    Retorna informações básicas como id, nome, login e status.
    """
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            logger.info("Executando consulta de usuários...")
            cur.execute(SQL_LIST_USERS)
            columns = [desc[0] for desc in cur.description]
            users = [dict(zip(columns, row)) for row in cur.fetchall()]
            cur.close()
            logger.info(f"Consulta retornou {len(users)} usuários")
            return users
    except Exception as e:
        logger.error(f"Erro detalhado ao listar usuários: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao consultar usuários: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consultar usuários")


@legacy_router.get("/pessoas", response_model=list[PessoaResponse], tags=["Pessoas"], summary="Listar pessoas")
def list_pessoas(skip: int = 0, limit: int = 100):
    """Lista pessoas cadastradas no sistema com suporte a paginação.
    
    Args:
        skip: Número de registros para pular (offset para paginação)
        limit: Número máximo de registros a retornar (max 100)
        
    Returns:
        Lista de pessoas com informações como id, nome, tipo, cpf, contatos e localização.
    """
    if limit > 100:
        limit = 100  # Limita o máximo de registros por questões de performance
        
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            # Query base com paginação como parâmetros
            paginated_query = SQL_LIST_PESSOAS.replace(';', '') + " LIMIT %(limit)s OFFSET %(offset)s;"
            cur.execute(paginated_query, {'limit': limit, 'offset': skip})
            columns = [desc[0] for desc in cur.description]
            pessoas = [dict(zip(columns, row)) for row in cur.fetchall()]
            cur.close()
            logger.info(f"Consulta retornou {len(pessoas)} pessoas (skip={skip}, limit={limit})")
            return pessoas
    except Exception as e:
        logger.error(f"Erro detalhado ao listar pessoas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar pessoas: {str(e)}"
        )

@legacy_router.get("/pessoas/cpf/{cpf}", response_model=PessoaResponse, tags=["Pessoas"], summary="Buscar pessoa por CPF")
def get_pessoa_by_cpf(cpf: str):
    """Busca uma pessoa específica pelo CPF.
    O CPF pode ser informado com ou sem máscara (ex: '123.456.789-00' ou '12345678900').
    """
    # Remove qualquer caractere não numérico do CPF
    cpf_digits = only_digits(cpf)
    
    if len(cpf_digits) != 11:
        raise HTTPException(
            status_code=400,
            detail="CPF inválido. Deve conter 11 dígitos."
        )
    
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(SQL_GET_PESSOA_BY_CPF, {"cpf_digits": cpf_digits})
            row = cur.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="Pessoa não encontrada com o CPF informado."
                )
            
            columns = [desc[0] for desc in cur.description]
            pessoa = dict(zip(columns, row))
            cur.close()
            return pessoa
    except HTTPException:
        raise  # Re-raise HTTP exceptions (404, etc)
    except Exception as e:
        logger.error(f"Erro ao buscar pessoa por CPF: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao consultar pessoa"
        )

@legacy_router.get("/pessoas/cnpj/{cnpj}", response_model=PessoaResponse, tags=["Pessoas"], summary="Buscar pessoa por CNPJ")
def get_pessoa_by_cnpj(cnpj: str):
    """Busca uma pessoa específica pelo CNPJ.
    O CNPJ pode ser informado com ou sem máscara (ex: '12.345.678/0001-90' ou '12345678000190').
    """
    # Remove qualquer caractere não numérico do CNPJ
    cnpj_digits = only_digits(cnpj)
    
    if len(cnpj_digits) != 14:
        raise HTTPException(
            status_code=400,
            detail="CNPJ inválido. Deve conter 14 dígitos."
        )
    
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            cur.execute(SQL_GET_PESSOA_BY_CNPJ, {"cnpj_digits": cnpj_digits})
            row = cur.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="Pessoa não encontrada com o CNPJ informado."
                )
            
            columns = [desc[0] for desc in cur.description]
            pessoa = dict(zip(columns, row))
            cur.close()
            return pessoa
    except HTTPException:
        raise  # Re-raise HTTP exceptions (404, etc)
    except Exception as e:
        logger.error(f"Erro ao buscar pessoa por CNPJ: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao consultar pessoa"
        )

@legacy_router.get("/imoveis", response_model=list[ImovelResponse], tags=["imoveis"], summary="Listar imóveis")
def list_imoveis(skip: int = 0, limit: int = 100):
    """Lista imóveis cadastrados no sistema.
    
    Args:
        skip: Número de registros para pular (offset para paginação)
        limit: Número máximo de registros a retornar (max 100)
        
    Returns:
        Lista de imóveis com informações como nome, área, localização e documentação.
    """
    if limit > 100:
        limit = 100  # Limita o máximo de registros por questões de performance
        
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            # Query base com paginação como parâmetros
            paginated_query = SQL_LIST_IMOVEIS.replace(';', '') + " LIMIT %(limit)s OFFSET %(offset)s;"
            cur.execute(paginated_query, {'limit': limit, 'offset': skip})
            columns = [desc[0] for desc in cur.description]
            imoveis = [dict(zip(columns, row)) for row in cur.fetchall()]
            cur.close()
            logger.info(f"Consulta retornou {len(imoveis)} imóveis (skip={skip}, limit={limit})")
            return imoveis
    except Exception as e:
        logger.error(f"Erro detalhado ao listar imóveis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar imóveis: {str(e)}"
        )

@legacy_router.get("/car", response_model=list[CarResponse], tags=["CAR"], summary="Listar CARs")
def list_car(skip: int = 0, limit: int = 100):
    """Lista CARs (Cadastro Ambiental Rural) cadastrados no sistema.
    
    Args:
        skip: Número de registros para pular (offset para paginação)
        limit: Número máximo de registros a retornar (max 100)
        
    Returns:
        Lista de CARs com informações como situação, imóvel associado e documentação.
    """
    if limit > 100:
        limit = 100  # Limita o máximo de registros por questões de performance
        
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            # Query base com paginação como parâmetros
            paginated_query = SQL_LIST_CAR.replace(';', '') + " LIMIT %(limit)s OFFSET %(offset)s;"
            cur.execute(paginated_query, {'limit': limit, 'offset': skip})
            columns = [desc[0] for desc in cur.description]
            cars = [dict(zip(columns, row)) for row in cur.fetchall()]
            cur.close()
            logger.info(f"Consulta retornou {len(cars)} CARs (skip={skip}, limit={limit})")
            return cars
    except Exception as e:
        logger.error(f"Erro detalhado ao listar CARs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar CARs: {str(e)}"
        )

@legacy_router.get("/pessoas/juridicas", response_model=list[PessoaResponse], tags=["Pessoas"], summary="Listar pessoas jurídicas ativas")
def list_pessoas_juridicas():
    """Lista todas as pessoas jurídicas ativas cadastradas."""
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    pkpessoa,
                    COALESCE(nome, razaosocial, nomefantasia) as nome,
                    razaosocial,
                    cnpj,
                    cidade as municipio,
                    fkestado,
                    status,
                    nomefantasia,
                    inscricaoestadual,
                    inscricaomunicipal,
                    email,
                    telefone,
                    tipo,
                    dtype
                FROM f_pessoa
                WHERE cnpj IS NOT NULL
                AND cnpj != ''
                ORDER BY razaosocial
            """)
            rows = cur.fetchall()
            if not rows:
                return []
            
            columns = [desc[0] for desc in cur.description]
            result = [dict(zip(columns, row)) for row in rows]
            cur.close()
            return result
    except Exception as e:
        logger.exception("Erro ao listar pessoas jurídicas")
        raise HTTPException(
            status_code=500,
            detail={"message": "Erro ao listar pessoas jurídicas", "error": str(e)}
        )

@legacy_router.post("/blockchain/register", response_model=BlockchainRegisterResponse, tags=["Blockchain"], 
          summary="Registrar dados no blockchain Continuus")
async def register_blockchain(payload: BlockchainRegisterRequest):
    """
    Registra dados no blockchain Continuus via API externa.
    
    Args:
        payload: Dados a serem registrados contendo IdBlockchain, Data e Fields
        
    Returns:
        Resposta do blockchain com status de sucesso/erro
        
    Exemplo de payload:
        {
            "IdBlockchain": 1,
            "Data": {
                "pkpessoa": "2001327",
                "cpf": "859.965.722-49",
                "nome": "João Silva"
            },
            "Fields": [
                {
                    "NmField": "LicenciamentoAmbientalPessoaFisica",
                    "DsValue": "Pessoa fisica do licenciamento ambiental"
                }
            ]
        }
    """
    BLOCKCHAIN_API_URL = "http://continuus.miltecti.com.br/continuus_api/api/Block/Register"
    BLOCKCHAIN_DSKEY = os.getenv("BLOCKCHAIN_DSKEY")
    
    if not BLOCKCHAIN_DSKEY:
        logger.error("BLOCKCHAIN_DSKEY não configurada no ambiente")
        return BlockchainRegisterResponse(
            success=False,
            message="Erro de configuração: chave de autenticação não encontrada",
            error="BLOCKCHAIN_DSKEY não está configurada no arquivo .env"
        )
    
    try:
        # Converte o payload para dict
        payload_dict = payload.model_dump()
        
        logger.info(f"Enviando dados para blockchain: IdBlockchain={payload.IdBlockchain}")
        
        # Criando headers com autenticação
        headers = {
            "Content-Type": "application/json",
            "dsKey": BLOCKCHAIN_DSKEY
        }
        
        # Faz a requisição POST para a API do blockchain
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                BLOCKCHAIN_API_URL,
                json=payload_dict,
                headers=headers
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            # Verifica se a requisição foi bem sucedida
            response.raise_for_status()
            
            # Tenta parsear a resposta como JSON
            try:
                blockchain_response = response.json()
            except Exception:
                blockchain_response = {"raw_response": response.text}
            
            logger.info(f"Blockchain registrado com sucesso: IdBlockchain={payload.IdBlockchain}")
            
            return BlockchainRegisterResponse(
                success=True,
                message="Dados registrados no blockchain com sucesso",
                blockchain_response=blockchain_response
            )
            
    except httpx.HTTPStatusError as e:
        error_detail = f"Erro HTTP {e.response.status_code}: {e.response.text}"
        logger.error(f"Erro ao comunicar com blockchain API: {error_detail}")
        
        return BlockchainRegisterResponse(
            success=False,
            message="Erro ao registrar no blockchain",
            error=error_detail
        )
        
    except httpx.RequestError as e:
        error_detail = f"Erro de conexão: {str(e)}"
        logger.error(f"Erro de requisição para blockchain API: {error_detail}")
        
        return BlockchainRegisterResponse(
            success=False,
            message="Erro de conexão com blockchain",
            error=error_detail
        )
        
    except Exception as e:
        error_detail = str(e)
        logger.exception("Erro inesperado ao registrar no blockchain")
        
        return BlockchainRegisterResponse(
            success=False,
            message="Erro inesperado",
            error=error_detail
        )

@legacy_router.post("/auth/login", response_model=LoginResponse, tags=["Auth"], summary="Autenticar usuário (CPF)")
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
# Montar routers
# -------------------------------------------------------
# Montar router legado com prefix configurável (auth, pessoas, car, blockchain, users)
# IMPORTANTE: Deve ser incluído DEPOIS das definições das rotas @legacy_router
app.include_router(legacy_router, prefix=settings.API_BASE)

# -------------------------------------------------------
# Execução local
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    # reload=True apenas em ambiente de desenvolvimento local
    # Em produção (Render), o uvicorn é executado diretamente via render.yaml
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
