"""
Configurações da aplicação usando Pydantic Settings.
Carrega variáveis de ambiente do arquivo .env.
"""
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Configurações gerais da aplicação."""
    
    # API Configuration
    API_BASE: str = Field(default="/api/v1", description="Base path para API v1")
    APP_NAME: str = Field(default="#licenciamentoambiental API", description="Nome da aplicação")
    APP_VERSION: str = Field(default="1.0.0", description="Versão da aplicação")
    
    # Supabase Configuration
    USE_SUPABASE_REST: bool = Field(default=True, description="Habilita uso do Supabase REST API")
    SUPABASE_URL: str = Field(default="", description="URL base do projeto Supabase")
    SUPABASE_REST_URL: str = Field(default="", description="URL do PostgREST do Supabase")
    SUPABASE_STORAGE_URL: str = Field(default="", description="URL do Storage do Supabase")
    SUPABASE_ANON_KEY: str = Field(default="", description="Anon key do Supabase")
    SUPABASE_SERVICE_ROLE: str = Field(default="", description="Service role key do Supabase")
    
    # CORS Configuration (will be parsed from CSV string)
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default="*",
        description="Lista de origens permitidas para CORS (separadas por vírgula no .env)"
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS_ORIGINS de CSV para lista."""
        if isinstance(v, str):
            # Se for string única "*", retornar como lista
            if v.strip() == "*":
                return ["*"]
            # Caso contrário, split por vírgula
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignora variáveis extras do .env (compatibilidade com configs existentes)
    )


# Instância global de configurações
settings = Settings()
