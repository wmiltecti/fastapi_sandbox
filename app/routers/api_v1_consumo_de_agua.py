"""
Router v1 para gerenciamento de Consumo de Água (Etapa 3 do Formulário).
Utiliza Supabase REST API via HTTP (não acesso direto ao banco).
"""
from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional
import logging

from app.config import settings
from app.supabase_proxy import base_headers, admin_headers, rest_post, rest_patch, rest_get, rest_delete
from app.schemas.consumo_de_agua_schemas import (
    ConsumoDeAguaUpsertRequest,
    ConsumoDeAguaResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/consumo-de-agua",
    tags=["v1-consumo-de-agua"]
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
    response_model=ConsumoDeAguaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar/Atualizar dados de Consumo de Água",
    description="""
    Cria ou atualiza dados de Consumo de Água (Etapa 3) para um processo.
    
    - Faz UPSERT dos dados de consumo de água
    - Relacionamento 1:1 com processo via processo_id
    - Retorna dados completos após inserção/atualização
    
    **Comportamento:**
    - Se já existem dados para o processo_id: atualiza
    - Se não existem: cria novo registro
    """
)
async def upsert_consumo_de_agua(
    dados: ConsumoDeAguaUpsertRequest,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    Endpoint para inserir ou atualizar dados completos de Consumo de Água.
    """
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Preparar dados para UPSERT
        consumo_agua_data = {
            "processo_id": dados.processo_id,
            "origem_rede_publica": dados.origem_rede_publica,
            "origem_poco_artesiano": dados.origem_poco_artesiano,
            "origem_poco_cacimba": dados.origem_poco_cacimba,
            "origem_captacao_superficial": dados.origem_captacao_superficial,
            "origem_captacao_pluvial": dados.origem_captacao_pluvial,
            "origem_caminhao_pipa": dados.origem_caminhao_pipa,
            "origem_outro": dados.origem_outro,
            "consumo_uso_humano_m3_dia": float(dados.consumo_uso_humano_m3_dia) if dados.consumo_uso_humano_m3_dia else None,
            "consumo_outros_usos_m3_dia": float(dados.consumo_outros_usos_m3_dia) if dados.consumo_outros_usos_m3_dia else None,
            "volume_despejo_diario_m3_dia": float(dados.volume_despejo_diario_m3_dia) if dados.volume_despejo_diario_m3_dia else None,
            "destino_final_efluente": dados.destino_final_efluente
        }
        
        # Tentar UPDATE primeiro
        headers_update = headers.copy()
        headers_update["Prefer"] = "return=representation"
        
        consumo_agua_response = await rest_patch(
            path=f"/f_form_consumo_de_agua?processo_id=eq.{dados.processo_id}",
            json=consumo_agua_data,
            headers=headers_update
        )
        
        # Se UPDATE não encontrou registro (lista vazia), fazer INSERT
        if not consumo_agua_response:
            headers_insert = headers.copy()
            headers_insert["Prefer"] = "return=representation"
            
            consumo_agua_response = await rest_post(
                path="/f_form_consumo_de_agua",
                json=consumo_agua_data,
                headers=headers_insert
            )
        
        if not consumo_agua_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to insert/update consumo de agua data"
            )
        
        # Pegar o primeiro item da resposta (que pode ser lista)
        consumo_agua_result = consumo_agua_response[0] if isinstance(consumo_agua_response, list) else consumo_agua_response
        
        logger.info(f"Successfully upserted consumo de agua for processo_id={dados.processo_id}")
        
        return ConsumoDeAguaResponse(**consumo_agua_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upserting consumo de agua: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error upserting consumo de agua: {str(e)}"
        )


@router.get(
    "/{processo_id}",
    response_model=ConsumoDeAguaResponse,
    summary="Buscar dados de Consumo de Água por processo_id",
    description="""
    Retorna os dados de Consumo de Água (Etapa 3) de um processo específico.
    
    - Busca por processo_id
    - Retorna 404 se não encontrado
    """
)
async def get_consumo_de_agua(
    processo_id: str,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    Endpoint para buscar dados de Consumo de Água por processo_id.
    """
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        response = await rest_get(
            path=f"/f_form_consumo_de_agua?processo_id=eq.{processo_id}",
            headers=headers
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consumo de agua data not found for processo_id={processo_id}"
            )
        
        consumo_agua_result = response[0] if isinstance(response, list) else response
        
        return ConsumoDeAguaResponse(**consumo_agua_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching consumo de agua: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching consumo de agua: {str(e)}"
        )


@router.delete(
    "/{processo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar dados de Consumo de Água",
    description="""
    Remove os dados de Consumo de Água (Etapa 3) de um processo.
    
    - Deleta por processo_id
    - Retorna 204 No Content em caso de sucesso
    - Retorna 404 se não encontrado
    """
)
async def delete_consumo_de_agua(
    processo_id: str,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """
    Endpoint para deletar dados de Consumo de Água por processo_id.
    """
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Verificar se existe
        existing = await rest_get(
            path=f"/f_form_consumo_de_agua?processo_id=eq.{processo_id}",
            headers=headers
        )
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consumo de agua data not found for processo_id={processo_id}"
            )
        
        # Deletar
        await rest_delete(
            path=f"/f_form_consumo_de_agua?processo_id=eq.{processo_id}",
            headers=headers
        )
        
        logger.info(f"Successfully deleted consumo de agua for processo_id={processo_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting consumo de agua: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting consumo de agua: {str(e)}"
        )
