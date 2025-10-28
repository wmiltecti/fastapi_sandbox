"""
Schemas Pydantic para processos de licenciamento ambiental.
Define modelos de request/response para a API v1.
"""
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ProcessoCreate(BaseModel):
    """Schema para criação de novo processo de licenciamento."""
    
    user_id: str = Field(..., description="ID do usuário criador do processo")
    status: str = Field(default="draft", description="Status inicial do processo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "123456",
                "status": "draft"
            }
        }
    )


class DadosGeraisUpsert(BaseModel):
    """
    Schema para inserir/atualizar dados gerais do processo (relação 1:1).
    Suporta tanto Pessoa Física quanto Jurídica.
    """
    
    processo_id: str = Field(..., description="ID do processo relacionado")
    
    # Tipo de pessoa
    tipo_pessoa: Optional[Literal["PF", "PJ"]] = Field(
        None,
        description="Tipo de pessoa: PF (Pessoa Física) ou PJ (Pessoa Jurídica)"
    )
    
    # Dados Pessoa Física
    cpf: Optional[str] = Field(None, description="CPF (somente números ou formatado)")
    
    # Dados Pessoa Jurídica
    cnpj: Optional[str] = Field(None, description="CNPJ (somente números ou formatado)")
    razao_social: Optional[str] = Field(None, description="Razão social da empresa")
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia da empresa")
    porte: Optional[str] = Field(None, description="Porte da empresa (MEI, ME, EPP, etc)")
    
    # Dados da Atividade
    potencial_poluidor: Optional[str] = Field(
        None,
        description="Potencial poluidor da atividade (baixo, médio, alto)"
    )
    descricao_resumo: Optional[str] = Field(
        None,
        description="Descrição resumida da atividade/empreendimento"
    )
    
    # Contatos
    contato_email: Optional[EmailStr] = Field(None, description="Email de contato")
    contato_telefone: Optional[str] = Field(None, description="Telefone de contato")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "processo_id": "proc_123",
                    "tipo_pessoa": "PF",
                    "cpf": "123.456.789-00",
                    "potencial_poluidor": "baixo",
                    "descricao_resumo": "Atividade agrícola de pequeno porte",
                    "contato_email": "contato@exemplo.com",
                    "contato_telefone": "(11) 98765-4321"
                },
                {
                    "processo_id": "proc_456",
                    "tipo_pessoa": "PJ",
                    "cnpj": "12.345.678/0001-90",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Exemplo Corp",
                    "porte": "ME",
                    "potencial_poluidor": "médio",
                    "descricao_resumo": "Indústria de transformação",
                    "contato_email": "empresa@exemplo.com",
                    "contato_telefone": "(11) 3333-4444"
                }
            ]
        }
    )


class LocalizacaoCreate(BaseModel):
    """
    Schema para adicionar localização ao processo (relação N:1).
    Um processo pode ter múltiplas localizações.
    """
    
    processo_id: str = Field(..., description="ID do processo relacionado")
    
    # Endereço
    endereco: Optional[str] = Field(None, description="Endereço completo")
    municipio_ibge: Optional[str] = Field(None, description="Código IBGE do município")
    uf: Optional[str] = Field(None, description="UF (sigla do estado)")
    cep: Optional[str] = Field(None, description="CEP")
    
    # Coordenadas geográficas
    latitude: Optional[float] = Field(None, description="Latitude (decimal)")
    longitude: Optional[float] = Field(None, description="Longitude (decimal)")
    
    # Informações adicionais
    referencia: Optional[str] = Field(
        None,
        description="Ponto de referência ou descrição adicional da localização"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "processo_id": "proc_123",
                "endereco": "Rua das Flores, 123 - Centro",
                "municipio_ibge": "1100015",
                "uf": "RO",
                "cep": "76801-000",
                "latitude": -8.7619,
                "longitude": -63.8999,
                "referencia": "Próximo ao mercado municipal"
            }
        }
    )


class WizardStatus(BaseModel):
    """Schema de resposta para status do wizard de cadastro."""
    
    id: str = Field(..., description="ID do processo")
    n_localizacoes: int = Field(default=0, description="Número de localizações cadastradas")
    n_atividades: int = Field(default=0, description="Número de atividades cadastradas")
    v_dados_gerais: bool = Field(default=False, description="Dados gerais preenchidos")
    v_resp_tecnico: bool = Field(default=False, description="Responsável técnico cadastrado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "proc_123",
                "n_localizacoes": 2,
                "n_atividades": 1,
                "v_dados_gerais": True,
                "v_resp_tecnico": True
            }
        }
    )
