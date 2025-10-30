"""
Schemas Pydantic para Uso de Recursos e Energia (Etapa 2 do Formulário).
Define modelos de request/response para a API v1.
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class CombustivelEnergiaItem(BaseModel):
    """Schema para item individual de combustível/energia."""
    
    tipo_fonte: str = Field(..., description="Tipo de fonte energética (Lenha, Gás Natural, Eletricidade, etc)")
    equipamento: str = Field(..., description="Equipamento que utiliza a energia (Caldeira Principal, Forno Industrial I, etc)")
    quantidade: Decimal = Field(..., description="Quantidade consumida", ge=0)
    unidade: str = Field(..., description="Unidade de medida (m³, MW, kWh, etc)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo_fonte": "Lenha",
                "equipamento": "Caldeira Principal",
                "quantidade": 250,
                "unidade": "m³"
            }
        }
    )


class CombustivelEnergiaResponse(CombustivelEnergiaItem):
    """Schema de resposta para item de combustível/energia (inclui ID)."""
    
    id: UUID
    processo_id: str
    created_at: str
    updated_at: str


class UsoRecursosEnergiaBase(BaseModel):
    """Schema base para dados de Uso de Recursos e Energia."""
    
    # Uso de Lenha
    usa_lenha: bool = Field(default=False, description="Utiliza lenha como combustível?")
    quantidade_lenha_m3: Optional[Decimal] = Field(None, description="Quantidade mensal de lenha em m³", ge=0)
    num_ceprof: Optional[str] = Field(None, description="Número do CEPROF (Cadastro Estadual de Produtores Florestais)")
    
    # Caldeira
    possui_caldeira: bool = Field(default=False, description="Possui caldeira?")
    altura_chamine_metros: Optional[Decimal] = Field(None, description="Altura da chaminé em metros", ge=0)
    
    # Fornos
    possui_fornos: bool = Field(default=False, description="Possui fornos?")
    sistema_captacao: Optional[str] = Field(None, description="Sistema de captação de emissões atmosféricas")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "usa_lenha": True,
                "quantidade_lenha_m3": 250,
                "num_ceprof": "CEPROF-12345",
                "possui_caldeira": True,
                "altura_chamine_metros": 15,
                "possui_fornos": True,
                "sistema_captacao": "Sistema de filtros ciclônicos com lavadores de gases"
            }
        }
    )


class UsoRecursosEnergiaCreate(UsoRecursosEnergiaBase):
    """Schema para criação de dados de Uso de Recursos e Energia."""
    
    processo_id: str = Field(..., description="ID do processo relacionado")


class UsoRecursosEnergiaUpdate(UsoRecursosEnergiaBase):
    """Schema para atualização de dados de Uso de Recursos e Energia."""
    
    pass


class UsoRecursosEnergiaResponse(UsoRecursosEnergiaBase):
    """Schema de resposta para dados de Uso de Recursos e Energia."""
    
    id: UUID
    processo_id: str
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


class UsoRecursosEnergiaCompleto(BaseModel):
    """Schema completo incluindo dados principais e lista de combustíveis/energia."""
    
    uso_recursos: UsoRecursosEnergiaResponse
    combustiveis_energia: List[CombustivelEnergiaResponse] = []
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "uso_recursos": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "processo_id": "PROC-2025-001",
                    "usa_lenha": True,
                    "quantidade_lenha_m3": 250,
                    "num_ceprof": "CEPROF-12345",
                    "possui_caldeira": True,
                    "altura_chamine_metros": 15,
                    "possui_fornos": True,
                    "sistema_captacao": "Sistema de filtros ciclônicos",
                    "created_at": "2025-10-30T10:00:00Z",
                    "updated_at": "2025-10-30T10:00:00Z"
                },
                "combustiveis_energia": [
                    {
                        "id": "223e4567-e89b-12d3-a456-426614174000",
                        "processo_id": "PROC-2025-001",
                        "tipo_fonte": "Lenha",
                        "equipamento": "Caldeira Principal",
                        "quantidade": 250,
                        "unidade": "m³",
                        "created_at": "2025-10-30T10:00:00Z",
                        "updated_at": "2025-10-30T10:00:00Z"
                    }
                ]
            }
        }
    )


class UsoRecursosEnergiaUpsertRequest(BaseModel):
    """Schema para inserir/atualizar dados completos de Uso de Recursos e Energia."""
    
    processo_id: str = Field(..., description="ID do processo relacionado")
    
    # Dados principais
    usa_lenha: bool = Field(default=False)
    quantidade_lenha_m3: Optional[Decimal] = Field(None, ge=0)
    num_ceprof: Optional[str] = None
    possui_caldeira: bool = Field(default=False)
    altura_chamine_metros: Optional[Decimal] = Field(None, ge=0)
    possui_fornos: bool = Field(default=False)
    sistema_captacao: Optional[str] = None
    
    # Lista de combustíveis e energia
    combustiveis_energia: List[CombustivelEnergiaItem] = Field(
        default=[],
        description="Lista de combustíveis e fontes de energia utilizados"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "processo_id": "PROC-2025-001",
                "usa_lenha": True,
                "quantidade_lenha_m3": 250,
                "num_ceprof": "CEPROF-12345",
                "possui_caldeira": True,
                "altura_chamine_metros": 15,
                "possui_fornos": True,
                "sistema_captacao": "Sistema de filtros ciclônicos com lavadores de gases",
                "combustiveis_energia": [
                    {
                        "tipo_fonte": "Lenha",
                        "equipamento": "Caldeira Principal",
                        "quantidade": 250,
                        "unidade": "m³"
                    },
                    {
                        "tipo_fonte": "Gás Natural",
                        "equipamento": "Forno Industrial I",
                        "quantidade": 500,
                        "unidade": "m³"
                    },
                    {
                        "tipo_fonte": "Eletricidade",
                        "equipamento": "Linha de Produção",
                        "quantidade": 2.5,
                        "unidade": "MW"
                    }
                ]
            }
        }
    )
