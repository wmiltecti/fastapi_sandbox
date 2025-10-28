"""
Cliente HTTP para Supabase PostgREST API.
Fornece funções para interagir com o Supabase via HTTP, respeitando RLS.
"""
from typing import Any, Optional, Dict
import httpx
from fastapi import HTTPException

from app.config import settings


def base_headers(user_bearer: Optional[str] = None) -> Dict[str, str]:
    """
    Gera headers base para requisições ao Supabase.
    
    Args:
        user_bearer: Token JWT do usuário (ex: "Bearer eyJ..."). 
                     Se fornecido, será repassado para o Supabase respeitar RLS.
    
    Returns:
        Dict com headers necessários para autenticação no Supabase.
    """
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Se o usuário está autenticado, repassa o JWT para o Supabase
    if user_bearer:
        headers["Authorization"] = user_bearer
    
    return headers


def admin_headers() -> Dict[str, str]:
    """
    Gera headers com permissões administrativas (bypass RLS).
    
    Returns:
        Dict com headers usando SERVICE_ROLE key.
    """
    return {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE}",
        "apikey": settings.SUPABASE_SERVICE_ROLE,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


async def rest_post(path: str, json: Any, headers: Dict[str, str]) -> Any:
    """
    Executa POST no Supabase PostgREST.
    
    Args:
        path: Caminho relativo (ex: "licenciamento.processo")
        json: Payload JSON a ser enviado
        headers: Headers de autenticação (use base_headers() ou admin_headers())
    
    Returns:
        Response JSON do Supabase
        
    Raises:
        HTTPException: Se status >= 400
    """
    url = f"{settings.SUPABASE_REST_URL}/{path}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=json, headers=headers)
            
            # Se erro, tenta extrair mensagem do Supabase
            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text
                
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Erro ao comunicar com Supabase: {str(e)}"
            )


async def rest_patch(path: str, json: Any, headers: Dict[str, str]) -> Any:
    """
    Executa PATCH no Supabase PostgREST.
    
    Args:
        path: Caminho relativo com query string (ex: "licenciamento.processo?id=eq.123")
        json: Payload JSON com campos a atualizar
        headers: Headers de autenticação
    
    Returns:
        Response JSON do Supabase
        
    Raises:
        HTTPException: Se status >= 400
    """
    url = f"{settings.SUPABASE_REST_URL}/{path}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.patch(url, json=json, headers=headers)
            
            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text
                
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Erro ao comunicar com Supabase: {str(e)}"
            )


async def rest_get(path: str, headers: Dict[str, str]) -> Any:
    """
    Executa GET no Supabase PostgREST.
    
    Args:
        path: Caminho relativo com query string (ex: "licenciamento.processo?id=eq.123")
        headers: Headers de autenticação
    
    Returns:
        Response JSON do Supabase (sempre uma lista)
        
    Raises:
        HTTPException: Se status >= 400
    """
    url = f"{settings.SUPABASE_REST_URL}/{path}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            
            if response.status_code >= 400:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text
                
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_detail
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Erro ao comunicar com Supabase: {str(e)}"
            )
