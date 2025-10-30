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
    
    # Protocolos e Identificação
    numero_processo_externo: Optional[str] = Field(
        None, 
        description="Número/protocolo do processo informado pelo usuário (opcional)"
    )
    # Nota: protocolo_interno é gerado automaticamente pelo banco
    # Nota: numero_processo_oficial é reservado para uso futuro (definição da analista)
    
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
    
    # Características do Empreendimento (Etapa 1 do Formulário)
    area_total: Optional[float] = Field(
        None,
        description="Área total do empreendimento em m²",
        ge=0
    )
    cnae_codigo: Optional[str] = Field(
        None,
        description="Código CNAE (ex: 1011-2/01)"
    )
    cnae_descricao: Optional[str] = Field(
        None,
        description="Descrição da atividade CNAE"
    )
    
    # Licença Anterior
    possui_licenca_anterior: Optional[bool] = Field(
        None,
        description="Indica se possui licença ambiental anterior"
    )
    tipo_licenca_anterior: Optional[str] = Field(
        None,
        description="Tipo de licença anterior (LO, LP, LI, etc)"
    )
    numero_licenca_anterior: Optional[str] = Field(
        None,
        description="Número da licença anterior"
    )
    ano_emissao_licenca: Optional[int] = Field(
        None,
        description="Ano de emissão da licença anterior",
        ge=1900,
        le=2100
    )
    validade_licenca: Optional[str] = Field(
        None,
        description="Data de validade da licença anterior (formato: YYYY-MM-DD)"
    )
    
    # Informações Operacionais
    numero_empregados: Optional[int] = Field(
        None,
        description="Número total de empregados",
        ge=0
    )
    horario_funcionamento_inicio: Optional[str] = Field(
        None,
        description="Horário de início do funcionamento (formato: HH:MM)"
    )
    horario_funcionamento_fim: Optional[str] = Field(
        None,
        description="Horário de término do funcionamento (formato: HH:MM)"
    )
    
    # Contatos
    contato_email: Optional[EmailStr] = Field(None, description="Email de contato")
    contato_telefone: Optional[str] = Field(None, description="Telefone de contato")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    # Pessoa Física - Exemplo completo
                    "processo_id": "550e8400-e29b-41d4-a716-446655440000",
                    "numero_processo_externo": "PROC-2025-001",
                    "tipo_pessoa": "PF",
                    "cpf": "123.456.789-00",
                    "cnpj": None,
                    "razao_social": None,
                    "nome_fantasia": None,
                    "porte": None,
                    "potencial_poluidor": "baixo",
                    "descricao_resumo": "Atividade agrícola de pequeno porte",
                    "area_total": 1500.5,
                    "cnae_codigo": "0111-3/01",
                    "cnae_descricao": "Cultivo de cereais",
                    "possui_licenca_anterior": False,
                    "tipo_licenca_anterior": None,
                    "numero_licenca_anterior": None,
                    "ano_emissao_licenca": None,
                    "validade_licenca": None,
                    "numero_empregados": 5,
                    "horario_funcionamento_inicio": "06:00",
                    "horario_funcionamento_fim": "18:00",
                    "contato_email": "contato@exemplo.com",
                    "contato_telefone": "(11) 98765-4321"
                },
                {
                    # Pessoa Jurídica - Exemplo completo
                    "processo_id": "550e8400-e29b-41d4-a716-446655440001",
                    "numero_processo_externo": "PROC-2025-002",
                    "tipo_pessoa": "PJ",
                    "cpf": None,
                    "cnpj": "12.345.678/0001-90",
                    "razao_social": "Empresa Exemplo LTDA",
                    "nome_fantasia": "Exemplo Corp",
                    "porte": "ME",
                    "potencial_poluidor": "médio",
                    "descricao_resumo": "Indústria de transformação - Frigorífico",
                    "area_total": 5000.0,
                    "cnae_codigo": "1011-2/01",
                    "cnae_descricao": "Frigorífico - abate de bovinos",
                    "possui_licenca_anterior": True,
                    "tipo_licenca_anterior": "LO - Licença de Operação",
                    "numero_licenca_anterior": "12345/2023",
                    "ano_emissao_licenca": 2023,
                    "validade_licenca": "2025-12-31",
                    "numero_empregados": 150,
                    "horario_funcionamento_inicio": "07:00",
                    "horario_funcionamento_fim": "17:00",
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


class DadosGeraisResponse(BaseModel):
    """Schema de resposta para dados gerais (inclui protocolos gerados)."""
    
    id: str = Field(..., description="UUID do registro")
    processo_id: str = Field(..., description="ID do processo relacionado")
    
    # Protocolos
    protocolo_interno: Optional[str] = Field(
        None, 
        description="Protocolo gerado automaticamente (formato: YYYY/NNNNNN)"
    )
    numero_processo_externo: Optional[str] = Field(
        None,
        description="Número do processo informado pelo usuário"
    )
    numero_processo_oficial: Optional[str] = Field(
        None,
        description="Número oficial do processo (reservado)"
    )
    
    # Demais campos
    tipo_pessoa: Optional[str] = None
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    porte: Optional[str] = None
    potencial_poluidor: Optional[str] = None
    descricao_resumo: Optional[str] = None
    contato_email: Optional[str] = None
    contato_telefone: Optional[str] = None
    
    # Características do Empreendimento (Etapa 1 do Formulário)
    area_total: Optional[float] = None
    cnae_codigo: Optional[str] = None
    cnae_descricao: Optional[str] = None
    
    # Licença Anterior
    possui_licenca_anterior: Optional[bool] = None
    tipo_licenca_anterior: Optional[str] = None
    numero_licenca_anterior: Optional[str] = None
    ano_emissao_licenca: Optional[int] = None
    validade_licenca: Optional[str] = None
    
    # Informações Operacionais
    numero_empregados: Optional[int] = None
    horario_funcionamento_inicio: Optional[str] = None
    horario_funcionamento_fim: Optional[str] = None
    
    created_at: Optional[str] = Field(None, description="Data de criação")
    updated_at: Optional[str] = Field(None, description="Data de atualização")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "processo_id": "672bd103-d854-4a33-8f11-de771c9a45be",
                "protocolo_interno": "2025/000001",
                "numero_processo_externo": "PROC-2025-001",
                "numero_processo_oficial": None,
                "tipo_pessoa": "PJ",
                "cnpj": "12.345.678/0001-90",
                "razao_social": "Empresa Exemplo LTDA",
                "nome_fantasia": "Exemplo Corp",
                "porte": "ME",
                "potencial_poluidor": "médio",
                "area_total": 5000.0,
                "cnae_codigo": "1011-2/01",
                "cnae_descricao": "Frigorífico - abate de bovinos",
                "possui_licenca_anterior": True,
                "tipo_licenca_anterior": "LO - Licença de Operação",
                "numero_licenca_anterior": "12345/2023",
                "ano_emissao_licenca": 2023,
                "validade_licenca": "2025-12-31",
                "numero_empregados": 150,
                "horario_funcionamento_inicio": "07:00",
                "horario_funcionamento_fim": "17:00",
                "contato_email": "empresa@exemplo.com",
                "contato_telefone": "(11) 3333-4444",
                "created_at": "2025-10-28T10:30:00Z",
                "updated_at": "2025-10-28T10:30:00Z"
            }
        }
    )

