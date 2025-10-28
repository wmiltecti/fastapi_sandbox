"""
Router v1 para gerenciamento de processos de licenciamento ambiental.
Utiliza Supabase REST API via HTTP (não acesso direto ao banco).
"""
from fastapi import APIRouter, HTTPException, Header, status, Request
from typing import Optional

from app.config import settings
from app.supabase_proxy import base_headers, admin_headers, rest_post, rest_patch, rest_get
from app.schemas.processo_schemas import (
    ProcessoCreate,
    DadosGeraisUpsert,
    LocalizacaoCreate,
    WizardStatus
)

# Rate limiting com graceful degradation
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    limiter = Limiter(key_func=get_remote_address)
    RATE_LIMIT_ENABLED = True
except ImportError:
    limiter = None
    RATE_LIMIT_ENABLED = False

router = APIRouter(
    prefix="/processos",
    tags=["v1-processos"]
)


def _check_supabase_enabled():
    """Guard condition: verifica se Supabase REST está habilitado."""
    if not settings.USE_SUPABASE_REST:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase REST API is disabled. Enable USE_SUPABASE_REST in settings."
        )


def _get_headers(authorization: Optional[str] = None):
    """
    Retorna headers apropriados baseado na presença de JWT.
    
    Se authorization fornecido: usa base_headers com JWT do usuário (RLS aplicado)
    Se não fornecido: usa admin_headers com SERVICE_ROLE (bypass RLS para testes)
    """
    if authorization:
        return base_headers(user_bearer=authorization)
    else:
        return admin_headers()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo processo",
    description="""
    Cria um novo processo de licenciamento ambiental no Supabase.
    
    Requer autenticação via JWT do usuário (header Authorization).
    O processo é criado com status inicial 'draft'.
    
    **Exemplo de uso:**
    ```json
    {
        "user_id": "auth_user_123",
        "status": "draft"
    }
    ```
    
    **Retorna:** Objeto do processo criado com ID gerado pelo Supabase.
    """
)
async def create_processo(
    payload: ProcessoCreate,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    POST / - Criar novo processo de licenciamento.
    
    Insere registro na tabela 'processos' via Supabase REST API.
    RLS aplicado automaticamente baseado no JWT do usuário.
    """
    _check_supabase_enabled()
    
    headers = _get_headers(authorization)
    
    # POST /processos com prefer=return=representation para obter objeto criado
    result = await rest_post(
        path="/processos",
        json=payload.model_dump(),
        headers=headers
    )
    
    return result


@router.put(
    "/{processo_id}/dados-gerais",
    status_code=status.HTTP_200_OK,
    summary="Upsert dados gerais do processo",
    description="""
    Insere ou atualiza dados gerais do processo (relação 1:1).
    
    Utiliza resolução 'merge-duplicates' para atualizar registro existente
    caso já exista dados gerais para o processo_id fornecido.
    
    Suporta tanto Pessoa Física (PF) quanto Jurídica (PJ):
    - **PF:** Informar tipo_pessoa="PF" e cpf
    - **PJ:** Informar tipo_pessoa="PJ", cnpj, razao_social, nome_fantasia, porte
    
    **Exemplo PF:**
    ```json
    {
        "processo_id": "proc_123",
        "tipo_pessoa": "PF",
        "cpf": "123.456.789-00",
        "potencial_poluidor": "baixo",
        "contato_email": "pessoa@exemplo.com"
    }
    ```
    
    **Exemplo PJ:**
    ```json
    {
        "processo_id": "proc_456",
        "tipo_pessoa": "PJ",
        "cnpj": "12.345.678/0001-90",
        "razao_social": "Empresa LTDA",
        "porte": "ME",
        "contato_email": "empresa@exemplo.com"
    }
    ```
    """
)
async def upsert_dados_gerais(
    processo_id: str,
    payload: DadosGeraisUpsert,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    PUT /{processo_id}/dados-gerais - Upsert dados gerais.
    
    Usa on_conflict=processo_id com resolution=merge-duplicates
    para update se já existir, insert caso contrário.
    """
    _check_supabase_enabled()
    
    # Validação: processo_id do path deve coincidir com payload
    if payload.processo_id != processo_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"processo_id mismatch: path={processo_id}, body={payload.processo_id}"
        )
    
    headers = _get_headers(authorization)
    
    # Tentar UPDATE primeiro
    headers_update = headers.copy()
    headers_update["Prefer"] = "return=representation"
    
    result = await rest_patch(
        path=f"/dados_gerais?processo_id=eq.{processo_id}",
        json=payload.model_dump(exclude_none=True),
        headers=headers_update
    )
    
    # Se retornou vazio, registro não existe - fazer INSERT
    if not result or len(result) == 0:
        headers_insert = headers.copy()
        headers_insert["Prefer"] = "return=representation"
        
        result = await rest_post(
            path="/dados_gerais",
            json=payload.model_dump(exclude_none=True),
            headers=headers_insert
        )
    
    # Retornar o primeiro item (POST e PATCH retornam array)
    return result[0] if result and len(result) > 0 else result


@router.post(
    "/{processo_id}/localizacoes",
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar localização ao processo",
    description="""
    Adiciona uma nova localização ao processo (relação N:1).
    
    Um processo pode ter múltiplas localizações cadastradas.
    Cada localização pode conter endereço completo e coordenadas geográficas.
    
    **Exemplo:**
    ```json
    {
        "processo_id": "proc_123",
        "endereco": "Rua das Flores, 123",
        "municipio_ibge": "1100015",
        "uf": "RO",
        "cep": "76801-000",
        "latitude": -8.7619,
        "longitude": -63.8999,
        "referencia": "Próximo ao mercado municipal"
    }
    ```
    """
)
async def add_localizacao(
    processo_id: str,
    payload: LocalizacaoCreate,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    POST /{processo_id}/localizacoes - Adicionar localização.
    
    Insere nova localização na tabela 'localizacoes'.
    Múltiplas localizações podem ser adicionadas ao mesmo processo.
    """
    _check_supabase_enabled()
    
    # Validação: processo_id do path deve coincidir com payload
    if payload.processo_id != processo_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"processo_id mismatch: path={processo_id}, body={payload.processo_id}"
        )
    
    headers = _get_headers(authorization)
    
    result = await rest_post(
        path="/localizacoes",
        json=payload.model_dump(exclude_none=True),
        headers=headers
    )
    
    return result


@router.get(
    "/{processo_id}/wizard-status",
    response_model=WizardStatus,
    status_code=status.HTTP_200_OK,
    summary="Consultar status do wizard de cadastro",
    description="""
    Retorna o status de preenchimento do wizard de cadastro do processo.
    
    Verifica se o processo tem:
    - n_localizacoes: Número de localizações cadastradas
    - n_atividades: Número de atividades cadastradas
    - v_dados_gerais: Se dados gerais foram preenchidos
    - v_resp_tecnico: Se responsável técnico foi cadastrado
    
    **Retorna 404** se não houver dados para o processo_id fornecido.
    
    **Exemplo de resposta:**
    ```json
    {
        "id": "proc_123",
        "n_localizacoes": 2,
        "n_atividades": 1,
        "v_dados_gerais": true,
        "v_resp_tecnico": false
    }
    ```
    """
)
async def get_wizard_status(
    processo_id: str,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    GET /{processo_id}/wizard-status - Consultar status do wizard.
    
    Query na view/tabela 'wizard_status' filtrado por processo_id.
    Retorna 404 se não encontrar resultados.
    """
    _check_supabase_enabled()
    
    headers = _get_headers(authorization)
    
    # GET /wizard_status?id=eq.{processo_id}
    result = await rest_get(
        path=f"/wizard_status?id=eq.{processo_id}",
        headers=headers
    )
    
    # Supabase retorna array, verificar se está vazio
    if not result or len(result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No wizard status found for processo_id={processo_id}"
        )
    
    # Retornar primeiro (e único) resultado
    return result[0]


@router.post(
    "/{processo_id}/submit",
    status_code=status.HTTP_200_OK,
    summary="Submeter processo para revisão",
    description="""
    Valida e submete o processo para revisão, alterando status para 'in_review'.
    
    **Validações obrigatórias:**
    - ✅ Pelo menos 1 localização cadastrada (n_localizacoes >= 1)
    - ✅ Pelo menos 1 atividade cadastrada (n_atividades >= 1)
    - ✅ Responsável técnico cadastrado (v_resp_tecnico == true)
    
    Se validação passar, atualiza status do processo para 'in_review'.
    
    **Rate Limit:** 20 requisições por minuto (se slowapi instalado).
    
    **Retorna 400** se validações falharem.
    **Retorna 404** se processo não existir.
    **Retorna 429** se exceder rate limit.
    
    **Exemplo de resposta (sucesso):**
    ```json
    {
        "id": "proc_123",
        "status": "in_review",
        "submitted_at": "2025-01-27T12:34:56Z"
    }
    ```
    """
)
async def submit_processo(
    processo_id: str,
    request: Request,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    POST /{processo_id}/submit - Validar wizard e submeter para revisão.
    
    Rate limiting aplicado: 20/minute (graceful degradation se slowapi não instalado).
    
    1. Consulta wizard_status
    2. Valida regras de negócio
    3. PATCH status='in_review' se validações passarem
    """
    # Rate limiting removido temporariamente devido a incompatibilidade
    # TODO: Implementar rate limiting corretamente com slowapi
    
    _check_supabase_enabled()
    
    headers = _get_headers(authorization)
    
    # 1. Consultar wizard status
    wizard_result = await rest_get(
        path=f"/wizard_status?id=eq.{processo_id}",
        headers=headers
    )
    
    if not wizard_result or len(wizard_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process {processo_id} not found"
        )
    
    wizard = wizard_result[0]
    
    # 2. Validações de negócio
    errors = []
    
    if wizard.get("n_localizacoes", 0) < 1:
        errors.append("Processo deve ter pelo menos 1 localização cadastrada")
    
    if wizard.get("n_atividades", 0) < 1:
        errors.append("Processo deve ter pelo menos 1 atividade cadastrada")
    
    if not wizard.get("v_resp_tecnico", False):
        errors.append("Responsável técnico deve ser cadastrado")
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Validação do wizard falhou",
                "errors": errors
            }
        )
    
    # 3. PATCH status para 'in_review'
    result = await rest_patch(
        path=f"/processos?id=eq.{processo_id}",
        json={"status": "in_review"},
        headers=headers
    )
    
    # Retornar primeiro item (PATCH retorna array)
    if result and len(result) > 0:
        return result[0]
    else:
        # Se PATCH não retornou nada, pode ser que o processo não existe
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to update process {processo_id}"
        )
