"""
Router v1 para gerenciamento de Pessoas (Físicas, Jurídicas e Estrangeiras).
Utiliza Supabase REST API via HTTP (não acesso direto ao banco).
"""
from fastapi import APIRouter, HTTPException, Header, status, Query
from typing import Optional, List, Union
import logging
from datetime import datetime

from app.config import settings
from app.supabase_proxy import base_headers, admin_headers, rest_post, rest_patch, rest_get, rest_delete
from app.schemas.pessoa_schemas import (
    PessoaFisicaCreate,
    PessoaJuridicaCreate,
    PessoaEstrangeiraCreate,
    PessoaResponse,
    PessoaUpdateRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/pessoas",
    tags=["v1-pessoas"]
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
    "/fisica",
    response_model=PessoaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar Pessoa Física",
    description="""
    Cadastra uma nova pessoa física no sistema.
    
    **Campos obrigatórios:**
    - CPF (com ou sem máscara)
    - Nome completo
    
    **Validações:**
    - CPF deve ter 11 dígitos
    - Email deve ser válido
    - Dados são inseridos na tabela f_pessoa
    """
)
async def criar_pessoa_fisica(
    dados: PessoaFisicaCreate,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """Endpoint para cadastrar pessoa física."""
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Preparar payload para inserção
        pessoa_data = {
            "tipo": 1,  # Pessoa Física
            "cpf": dados.cpf,
            "nome": dados.nome,
            "datanascimento": dados.datanascimento.isoformat() if dados.datanascimento else None,
            "rg": dados.rg,
            "orgaoemissor": dados.orgaoemissor,
            "fkestadoemissor": dados.fkestadoemissor,
            "naturalidade": dados.naturalidade,
            "nacionalidade": dados.nacionalidade,
            "estadocivil": dados.estadocivil,
            "sexo": dados.sexo,
            "profissao": dados.profissao,
            "fkprofissao": dados.fkprofissao,
            "filiacaomae": dados.filiacaomae,
            "filiacaopai": dados.filiacaopai,
            "passaporte": dados.passaporte,
            "datapassaporte": dados.datapassaporte.isoformat() if dados.datapassaporte else None,
            "telefone": dados.telefone,
            "telefonealternativo1": dados.telefonealternativo1,
            "telefonealternativo2": dados.telefonealternativo2,
            "email": dados.email,
            "emailalternativo": dados.emailalternativo,
            "fax": dados.fax,
            "endereco": dados.endereco,
            "complemento": dados.complemento,
            "cep": dados.cep,
            "cidade": dados.cidade,
            "fkestado": dados.fkestado,
            "fkmunicipio": dados.fkmunicipio,
            "fkpais": dados.fkpais,
            "caixapostal": dados.caixapostal,
            "status": dados.status,
            "datacadastro": datetime.now().isoformat()
        }
        
        # Remover campos None
        pessoa_data = {k: v for k, v in pessoa_data.items() if v is not None}
        
        headers_insert = headers.copy()
        headers_insert["Prefer"] = "return=representation"
        
        response = await rest_post(
            path="/f_pessoa",
            json=pessoa_data,
            headers=headers_insert
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create pessoa fisica"
            )
        
        result = response[0] if isinstance(response, list) else response
        
        logger.info(f"Successfully created pessoa fisica with CPF={dados.cpf}")
        
        return PessoaResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating pessoa fisica: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating pessoa fisica: {str(e)}"
        )


@router.post(
    "/juridica",
    response_model=PessoaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar Pessoa Jurídica",
    description="""
    Cadastra uma nova pessoa jurídica no sistema.
    
    **Campos obrigatórios:**
    - CNPJ (com ou sem máscara)
    - Razão Social
    
    **Validações:**
    - CNPJ deve ter 14 dígitos
    - Email deve ser válido
    - Dados são inseridos na tabela f_pessoa
    """
)
async def criar_pessoa_juridica(
    dados: PessoaJuridicaCreate,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """Endpoint para cadastrar pessoa jurídica."""
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Preparar payload para inserção
        pessoa_data = {
            "tipo": 2,  # Pessoa Jurídica
            "cnpj": dados.cnpj,
            "razaosocial": dados.razaosocial,
            "nome": dados.nome or dados.razaosocial,  # nome pode ser igual à razão social
            "nomefantasia": dados.nomefantasia,
            "inscricaoestadual": dados.inscricaoestadual,
            "fkufinscricaoestadual": dados.fkufinscricaoestadual,
            "inscricaomunicipal": dados.inscricaomunicipal,
            "cnaefiscal": dados.cnaefiscal,
            "datainicioatividade": dados.datainicioatividade.isoformat() if dados.datainicioatividade else None,
            "fknaturezajuridica": dados.fknaturezajuridica,
            "fkporte": dados.fkporte,
            "porteempresa": dados.porteempresa,
            "situacaopessoajuridica": dados.situacaopessoajuridica,
            "simplesnacional": dados.simplesnacional,
            "crccontador": dados.crccontador,
            "telefone": dados.telefone,
            "telefonealternativo1": dados.telefonealternativo1,
            "telefonealternativo2": dados.telefonealternativo2,
            "email": dados.email,
            "emailalternativo": dados.emailalternativo,
            "fax": dados.fax,
            "endereco": dados.endereco,
            "complemento": dados.complemento,
            "cep": dados.cep,
            "cidade": dados.cidade,
            "fkestado": dados.fkestado,
            "fkmunicipio": dados.fkmunicipio,
            "fkpais": dados.fkpais,
            "caixapostal": dados.caixapostal,
            "status": dados.status,
            "datacadastro": datetime.now().isoformat()
        }
        
        # Remover campos None
        pessoa_data = {k: v for k, v in pessoa_data.items() if v is not None}
        
        headers_insert = headers.copy()
        headers_insert["Prefer"] = "return=representation"
        
        response = await rest_post(
            path="/f_pessoa",
            json=pessoa_data,
            headers=headers_insert
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create pessoa juridica"
            )
        
        result = response[0] if isinstance(response, list) else response
        
        logger.info(f"Successfully created pessoa juridica with CNPJ={dados.cnpj}")
        
        return PessoaResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating pessoa juridica: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating pessoa juridica: {str(e)}"
        )


@router.post(
    "/estrangeira",
    response_model=PessoaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar Pessoa Estrangeira",
    description="""
    Cadastra uma nova pessoa estrangeira no sistema.
    
    **Campos obrigatórios:**
    - Identificação Estrangeira (RNE, RNM, etc)
    - Nome completo
    
    **Validações:**
    - Email deve ser válido
    - Dados são inseridos na tabela f_pessoa
    """
)
async def criar_pessoa_estrangeira(
    dados: PessoaEstrangeiraCreate,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """Endpoint para cadastrar pessoa estrangeira."""
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Preparar payload para inserção
        pessoa_data = {
            "tipo": 3,  # Estrangeiro
            "identificacaoestrangeira": dados.identificacaoestrangeira,
            "tipoidentificacaoestrangeira": dados.tipoidentificacaoestrangeira,
            "nome": dados.nome,
            "datanascimento": dados.datanascimento.isoformat() if dados.datanascimento else None,
            "nacionalidade": dados.nacionalidade,
            "passaporte": dados.passaporte,
            "datapassaporte": dados.datapassaporte.isoformat() if dados.datapassaporte else None,
            "telefone": dados.telefone,
            "telefonealternativo1": dados.telefonealternativo1,
            "telefonealternativo2": dados.telefonealternativo2,
            "email": dados.email,
            "emailalternativo": dados.emailalternativo,
            "endereco": dados.endereco,
            "complemento": dados.complemento,
            "cep": dados.cep,
            "cidade": dados.cidade,
            "fkestado": dados.fkestado,
            "fkmunicipio": dados.fkmunicipio,
            "fkpais": dados.fkpais,
            "caixapostal": dados.caixapostal,
            "status": dados.status,
            "datacadastro": datetime.now().isoformat()
        }
        
        # Remover campos None
        pessoa_data = {k: v for k, v in pessoa_data.items() if v is not None}
        
        headers_insert = headers.copy()
        headers_insert["Prefer"] = "return=representation"
        
        response = await rest_post(
            path="/f_pessoa",
            json=pessoa_data,
            headers=headers_insert
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create pessoa estrangeira"
            )
        
        result = response[0] if isinstance(response, list) else response
        
        logger.info(f"Successfully created pessoa estrangeira")
        
        return PessoaResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating pessoa estrangeira: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating pessoa estrangeira: {str(e)}"
        )


@router.get(
    "",
    response_model=List[PessoaResponse],
    summary="Listar pessoas",
    description="""
    Lista pessoas cadastradas no sistema com filtros e paginação.
    
    **Filtros disponíveis:**
    - tipo: 1=Física, 2=Jurídica, 3=Estrangeiro
    - status: 1=Ativo, 0=Inativo
    - limit e offset para paginação
    """
)
async def listar_pessoas(
    tipo: Optional[int] = Query(None, description="Tipo de pessoa (1=Física, 2=Jurídica, 3=Estrangeiro)"),
    status: Optional[int] = Query(None, description="Status (1=Ativo, 0=Inativo)"),
    limit: int = Query(100, le=100, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Número de registros para pular"),
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """Endpoint para listar pessoas com filtros."""
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Construir query params
        query_params = []
        
        if tipo is not None:
            query_params.append(f"tipo=eq.{tipo}")
        
        if status is not None:
            query_params.append(f"status=eq.{status}")
        
        # Adicionar paginação
        query_params.append(f"limit={limit}")
        query_params.append(f"offset={offset}")
        
        # Ordenação
        query_params.append("order=pkpessoa.desc")
        
        query_string = "&".join(query_params)
        path = f"/f_pessoa?{query_string}"
        
        response = await rest_get(path=path, headers=headers)
        
        if not response:
            return []
        
        return [PessoaResponse(**item) for item in response]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing pessoas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing pessoas: {str(e)}"
        )


@router.get(
    "/{pkpessoa}",
    response_model=PessoaResponse,
    summary="Buscar pessoa por ID",
    description="""
    Busca uma pessoa específica pelo ID (pkpessoa).
    
    Retorna 404 se não encontrado.
    """
)
async def buscar_pessoa(
    pkpessoa: int,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """Endpoint para buscar pessoa por ID."""
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        response = await rest_get(
            path=f"/f_pessoa?pkpessoa=eq.{pkpessoa}",
            headers=headers
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pessoa not found with pkpessoa={pkpessoa}"
            )
        
        result = response[0] if isinstance(response, list) else response
        
        return PessoaResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pessoa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pessoa: {str(e)}"
        )


@router.put(
    "/{pkpessoa}",
    response_model=PessoaResponse,
    summary="Atualizar pessoa",
    description="""
    Atualiza os dados de uma pessoa existente.
    
    Apenas os campos fornecidos serão atualizados.
    Campos não fornecidos permanecerão inalterados.
    """
)
async def atualizar_pessoa(
    pkpessoa: int,
    dados: PessoaUpdateRequest,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """Endpoint para atualizar pessoa."""
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Verificar se pessoa existe
        existing = await rest_get(
            path=f"/f_pessoa?pkpessoa=eq.{pkpessoa}",
            headers=headers
        )
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pessoa not found with pkpessoa={pkpessoa}"
            )
        
        # Preparar dados para atualização (apenas campos fornecidos)
        update_data = dados.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Adicionar timestamp de atualização
        update_data["dataultimaalteracao"] = datetime.now().isoformat()
        
        headers_update = headers.copy()
        headers_update["Prefer"] = "return=representation"
        
        response = await rest_patch(
            path=f"/f_pessoa?pkpessoa=eq.{pkpessoa}",
            json=update_data,
            headers=headers_update
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pessoa"
            )
        
        result = response[0] if isinstance(response, list) else response
        
        logger.info(f"Successfully updated pessoa pkpessoa={pkpessoa}")
        
        return PessoaResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pessoa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating pessoa: {str(e)}"
        )


@router.delete(
    "/{pkpessoa}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar pessoa",
    description="""
    Remove uma pessoa do sistema (exclusão física).
    
    ⚠️ ATENÇÃO: Esta operação é irreversível.
    
    Recomenda-se usar inativação (status=0) ao invés de exclusão.
    """
)
async def deletar_pessoa(
    pkpessoa: int,
    authorization: Optional[str] = Header(None, description="Bearer token JWT do usuário")
):
    """Endpoint para deletar pessoa."""
    _check_supabase_enabled()
    headers = _get_headers(authorization)
    
    try:
        # Verificar se pessoa existe
        existing = await rest_get(
            path=f"/f_pessoa?pkpessoa=eq.{pkpessoa}",
            headers=headers
        )
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pessoa not found with pkpessoa={pkpessoa}"
            )
        
        # Deletar
        await rest_delete(
            path=f"/f_pessoa?pkpessoa=eq.{pkpessoa}",
            headers=headers
        )
        
        logger.info(f"Successfully deleted pessoa pkpessoa={pkpessoa}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pessoa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting pessoa: {str(e)}"
        )
