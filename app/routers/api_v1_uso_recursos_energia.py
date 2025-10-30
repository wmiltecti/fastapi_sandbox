"""
Router v1 para gerenciamento de Uso de Recursos e Energia (Etapa 2 do Formulário).
Utiliza Supabase REST API via HTTP (não acesso direto ao banco).
"""
from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional, List
import logging

from app.config import settings
from app.supabase_proxy import base_headers, admin_headers, rest_post, rest_patch, rest_get, rest_delete
from app.schemas.uso_recursos_energia_schemas import (
    UsoRecursosEnergiaUpsertRequest,
    UsoRecursosEnergiaCompleto,
    UsoRecursosEnergiaResponse,
    CombustivelEnergiaResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/uso-recursos-energia",
    tags=["v1-uso-recursos-energia"]
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
        headers = base_headers()
        headers["Authorization"] = authorization
        return headers
    return admin_headers()


@router.post(
    "",
    response_model=UsoRecursosEnergiaCompleto,
    status_code=status.HTTP_201_CREATED,
    summary="Criar/Atualizar dados de Uso de Recursos e Energia",
    description="""
    Cria ou atualiza dados de Uso de Recursos e Energia (Etapa 2) para um processo.
    
    - Faz UPSERT dos dados principais (uso_recursos_energia)
    - Substitui completamente a lista de combustíveis/energia
    - Relacionamento 1:1 com processo via processo_id
    - Retorna dados completos após inserção/atualização
    
    **Comportamento:**
    - Se já existem dados para o processo_id: atualiza
    - Se não existem: cria novo registro
    - Lista de combustíveis é sempre substituída por completo
    """
)
async def upsert_uso_recursos_energia(
    dados: UsoRecursosEnergiaUpsertRequest,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    Endpoint para inserir ou atualizar dados completos de Uso de Recursos e Energia.
    """
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # 1. UPSERT na tabela uso_recursos_energia (dados principais)
        uso_recursos_data = {
            "processo_id": dados.processo_id,
            "usa_lenha": dados.usa_lenha,
            "quantidade_lenha_m3": float(dados.quantidade_lenha_m3) if dados.quantidade_lenha_m3 else None,
            "num_ceprof": dados.num_ceprof,
            "possui_caldeira": dados.possui_caldeira,
            "altura_chamine_metros": float(dados.altura_chamine_metros) if dados.altura_chamine_metros else None,
            "possui_fornos": dados.possui_fornos,
            "sistema_captacao": dados.sistema_captacao
        }
        
        # Tentar UPDATE primeiro
        headers_update = headers.copy()
        headers_update["Prefer"] = "return=representation"
        
        uso_recursos_response = await rest_patch(
            path=f"/f_form_uso_recursos_energia?processo_id=eq.{dados.processo_id}",
            json=uso_recursos_data,
            headers=headers_update
        )
        
        # Se retornou vazio, registro não existe - fazer INSERT
        if not uso_recursos_response or len(uso_recursos_response) == 0:
            headers_insert = headers.copy()
            headers_insert["Prefer"] = "return=representation"
            
            uso_recursos_response = await rest_post(
                path="/f_form_uso_recursos_energia",
                json=uso_recursos_data,
                headers=headers_insert
            )
        
        if not uso_recursos_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao criar/atualizar dados de uso de recursos e energia"
            )
        
        # 2. Deletar combustíveis/energia existentes do processo
        await rest_delete(
            f"/f_form_combustiveis_energia?processo_id=eq.{dados.processo_id}",
            headers=headers
        )
        
        # 3. Inserir novos combustíveis/energia
        combustiveis_response = []
        if dados.combustiveis_energia:
            combustiveis_data = [
                {
                    "processo_id": dados.processo_id,
                    "tipo_fonte": item.tipo_fonte,
                    "equipamento": item.equipamento,
                    "quantidade": float(item.quantidade),
                    "unidade": item.unidade
                }
                for item in dados.combustiveis_energia
            ]
            
            headers_insert = headers.copy()
            headers_insert["Prefer"] = "return=representation"
            
            combustiveis_response = await rest_post(
                path="/f_form_combustiveis_energia",
                json=combustiveis_data,
                headers=headers_insert
            )
        
        # 4. Retornar resposta completa
        return UsoRecursosEnergiaCompleto(
            uso_recursos=UsoRecursosEnergiaResponse(**uso_recursos_response[0]),
            combustiveis_energia=[
                CombustivelEnergiaResponse(**item) for item in (combustiveis_response or [])
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar upsert de uso_recursos_energia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar dados: {str(e)}"
        )


@router.get(
    "/{processo_id}",
    response_model=UsoRecursosEnergiaCompleto,
    summary="Buscar dados de Uso de Recursos e Energia por processo",
    description="""
    Retorna dados completos de Uso de Recursos e Energia de um processo.
    
    - Busca dados principais (uso_recursos_energia)
    - Busca lista de combustíveis/energia relacionados
    - Retorna 404 se processo não possui dados de Etapa 2
    """
)
async def get_uso_recursos_energia(
    processo_id: str,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    Endpoint para buscar dados de Uso de Recursos e Energia de um processo.
    """
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # 1. Buscar dados principais
        uso_recursos_response = await rest_get(
            f"/f_form_uso_recursos_energia?processo_id=eq.{processo_id}&select=*",
            headers=headers
        )
        
        if not uso_recursos_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dados de uso de recursos e energia não encontrados para processo {processo_id}"
            )
        
        # 2. Buscar combustíveis/energia
        combustiveis_response = await rest_get(
            f"/f_form_combustiveis_energia?processo_id=eq.{processo_id}&select=*&order=created_at.asc",
            headers=headers
        )
        
        # 3. Retornar resposta completa
        return UsoRecursosEnergiaCompleto(
            uso_recursos=UsoRecursosEnergiaResponse(**uso_recursos_response[0]),
            combustiveis_energia=[
                CombustivelEnergiaResponse(**item) for item in (combustiveis_response or [])
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar uso_recursos_energia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar dados: {str(e)}"
        )


@router.delete(
    "/{processo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar dados de Uso de Recursos e Energia",
    description="""
    Remove todos os dados de Uso de Recursos e Energia de um processo.
    
    - Delete em cascata remove automaticamente combustíveis/energia relacionados
    - Retorna 204 No Content em sucesso
    """
)
async def delete_uso_recursos_energia(
    processo_id: str,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    Endpoint para deletar dados de Uso de Recursos e Energia de um processo.
    """
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Delete principal (cascata remove combustíveis automaticamente)
        await rest_delete(
            f"/f_form_uso_recursos_energia?processo_id=eq.{processo_id}",
            headers=headers
        )
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao deletar uso_recursos_energia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar dados: {str(e)}"
        )
