"""
Schemas Pydantic para Consumo de Água (Etapa 3 do Formulário).
Define modelos de request/response para a API v1.
"""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class ConsumoDeAguaBase(BaseModel):
    """Schema base para dados de Consumo de Água."""
    
    # Origem da Água (múltiplas seleções possíveis)
    origem_rede_publica: bool = Field(default=False, description="Origem: Rede Pública")
    origem_poco_artesiano: bool = Field(default=False, description="Origem: Poço Artesiano")
    origem_poco_cacimba: bool = Field(default=False, description="Origem: Poço Cacimba")
    origem_captacao_superficial: bool = Field(default=False, description="Origem: Captação Superficial")
    origem_captacao_pluvial: bool = Field(default=False, description="Origem: Captação Pluvial")
    origem_caminhao_pipa: bool = Field(default=False, description="Origem: Caminhão Pipa")
    origem_outro: bool = Field(default=False, description="Origem: Outro")
    
    # Consumo de Água
    consumo_uso_humano_m3_dia: Optional[Decimal] = Field(
        None, 
        description="Consumo de água para uso humano em m³/dia", 
        ge=0
    )
    consumo_outros_usos_m3_dia: Optional[Decimal] = Field(
        None, 
        description="Consumo de água para outros usos em m³/dia", 
        ge=0
    )
    
    # Efluentes
    volume_despejo_diario_m3_dia: Optional[Decimal] = Field(
        None, 
        description="Volume de despejo diário em m³/dia", 
        ge=0
    )
    destino_final_efluente: Optional[str] = Field(
        None, 
        description="Destino final do efluente"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "origem_rede_publica": True,
                "origem_poco_artesiano": False,
                "origem_poco_cacimba": False,
                "origem_captacao_superficial": True,
                "origem_captacao_pluvial": False,
                "origem_caminhao_pipa": False,
                "origem_outro": False,
                "consumo_uso_humano_m3_dia": 15.5,
                "consumo_outros_usos_m3_dia": 25.0,
                "volume_despejo_diario_m3_dia": 35.0,
                "destino_final_efluente": "Rede de Esgoto Municipal"
            }
        }
    )


class ConsumoDeAguaCreate(ConsumoDeAguaBase):
    """Schema para criação de dados de Consumo de Água."""
    
    processo_id: str = Field(..., description="ID do processo relacionado")


class ConsumoDeAguaUpdate(ConsumoDeAguaBase):
    """Schema para atualização de dados de Consumo de Água."""
    
    pass


class ConsumoDeAguaResponse(ConsumoDeAguaBase):
    """Schema de resposta para dados de Consumo de Água."""
    
    id: UUID
    processo_id: str
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


class ConsumoDeAguaUpsertRequest(ConsumoDeAguaBase):
    """
    Schema para requisição de UPSERT (create ou update) de dados de Consumo de Água.
    Utilizado no endpoint POST principal.
    """
    
    processo_id: str = Field(..., description="ID do processo relacionado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "processo_id": "PROC-2025-001234",
                "origem_rede_publica": True,
                "origem_poco_artesiano": False,
                "origem_poco_cacimba": False,
                "origem_captacao_superficial": True,
                "origem_captacao_pluvial": False,
                "origem_caminhao_pipa": False,
                "origem_outro": False,
                "consumo_uso_humano_m3_dia": 15.5,
                "consumo_outros_usos_m3_dia": 25.0,
                "volume_despejo_diario_m3_dia": 35.0,
                "destino_final_efluente": "Rede de Esgoto Municipal"
            }
        }
    )
