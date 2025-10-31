"""
Schemas Pydantic para Pessoas (Cadastro de Pessoas Físicas e Jurídicas).
Define modelos de request/response para a API v1.
"""
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from uuid import UUID
import re


def validar_cpf(cpf: str) -> str:
    """Remove caracteres não numéricos do CPF e valida tamanho."""
    cpf_digits = re.sub(r'\D', '', cpf)
    if len(cpf_digits) != 11:
        raise ValueError('CPF deve conter 11 dígitos')
    return cpf_digits


def validar_cnpj(cnpj: str) -> str:
    """Remove caracteres não numéricos do CNPJ e valida tamanho."""
    cnpj_digits = re.sub(r'\D', '', cnpj)
    if len(cnpj_digits) != 14:
        raise ValueError('CNPJ deve conter 14 dígitos')
    return cnpj_digits


class PessoaBase(BaseModel):
    """Schema base para dados comuns de pessoa física e jurídica."""
    
    # Campos comuns
    tipo: int = Field(..., description="Tipo de pessoa (1=Física, 2=Jurídica)")
    nome: Optional[str] = Field(None, max_length=150, description="Nome completo (pessoa física) ou razão social (jurídica)")
    
    # Contatos
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone principal")
    telefonealternativo1: Optional[str] = Field(None, max_length=20, description="Telefone alternativo 1")
    telefonealternativo2: Optional[str] = Field(None, max_length=20, description="Telefone alternativo 2")
    email: Optional[EmailStr] = Field(None, description="E-mail principal")
    emailalternativo: Optional[EmailStr] = Field(None, description="E-mail alternativo")
    fax: Optional[str] = Field(None, max_length=20, description="Fax")
    
    # Endereço
    endereco: Optional[str] = Field(None, max_length=800, description="Endereço completo")
    complemento: Optional[str] = Field(None, max_length=80, description="Complemento do endereço")
    cep: Optional[str] = Field(None, max_length=14, description="CEP")
    cidade: Optional[str] = Field(None, max_length=50, description="Cidade")
    fkestado: Optional[int] = Field(None, description="FK do estado")
    fkmunicipio: Optional[int] = Field(None, description="FK do município")
    fkpais: Optional[int] = Field(None, description="FK do país")
    caixapostal: Optional[str] = Field(None, max_length=10, description="Caixa postal")
    
    # Status
    status: Optional[int] = Field(1, description="Status da pessoa (1=Ativo, 0=Inativo)")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "tipo": 1,
                "nome": "João Silva Santos",
                "telefone": "(11) 98765-4321",
                "email": "joao.silva@email.com",
                "endereco": "Rua das Flores, 123",
                "cep": "01234-567",
                "cidade": "São Paulo",
                "status": 1
            }
        }
    )


class PessoaFisicaCreate(PessoaBase):
    """Schema para criação de Pessoa Física."""
    
    tipo: int = Field(1, description="Tipo fixo: 1 (Pessoa Física)")
    
    # Identificação
    cpf: str = Field(..., description="CPF (somente números ou com máscara)")
    rg: Optional[str] = Field(None, max_length=14, description="RG")
    orgaoemissor: Optional[str] = Field(None, max_length=50, description="Órgão emissor do RG")
    fkestadoemissor: Optional[int] = Field(None, description="FK do estado emissor")
    
    # Dados pessoais
    datanascimento: Optional[date] = Field(None, description="Data de nascimento")
    naturalidade: Optional[str] = Field(None, max_length=30, description="Naturalidade")
    nacionalidade: Optional[str] = Field(None, max_length=30, description="Nacionalidade")
    estadocivil: Optional[int] = Field(None, description="Estado civil")
    sexo: Optional[int] = Field(None, description="Sexo (1=Masculino, 2=Feminino)")
    filiacaomae: Optional[str] = Field(None, max_length=150, description="Nome da mãe")
    filiacaopai: Optional[str] = Field(None, max_length=150, description="Nome do pai")
    
    # Profissão
    profissao: Optional[str] = Field(None, max_length=100, description="Profissão")
    fkprofissao: Optional[int] = Field(None, description="FK da profissão")
    
    # Estrangeiro
    passaporte: Optional[str] = Field(None, max_length=18, description="Número do passaporte")
    datapassaporte: Optional[date] = Field(None, description="Data de emissão do passaporte")
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        return validar_cpf(v)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo": 1,
                "cpf": "123.456.789-00",
                "nome": "João Silva Santos",
                "datanascimento": "1990-05-15",
                "rg": "12.345.678-9",
                "orgaoemissor": "SSP",
                "telefone": "(11) 98765-4321",
                "email": "joao.silva@email.com",
                "endereco": "Rua das Flores, 123",
                "cep": "01234-567",
                "cidade": "São Paulo",
                "sexo": 1,
                "estadocivil": 1,
                "profissao": "Engenheiro",
                "status": 1
            }
        }
    )


class PessoaJuridicaCreate(PessoaBase):
    """Schema para criação de Pessoa Jurídica."""
    
    tipo: int = Field(2, description="Tipo fixo: 2 (Pessoa Jurídica)")
    
    # Identificação
    cnpj: str = Field(..., description="CNPJ (somente números ou com máscara)")
    razaosocial: str = Field(..., max_length=150, description="Razão social")
    nomefantasia: Optional[str] = Field(None, max_length=150, description="Nome fantasia")
    
    # Inscrições
    inscricaoestadual: Optional[str] = Field(None, max_length=18, description="Inscrição estadual")
    fkufinscricaoestadual: Optional[int] = Field(None, description="FK UF da inscrição estadual")
    inscricaomunicipal: Optional[str] = Field(None, max_length=18, description="Inscrição municipal")
    
    # Dados empresariais
    cnaefiscal: Optional[str] = Field(None, max_length=14, description="CNAE Fiscal")
    datainicioatividade: Optional[date] = Field(None, description="Data de início de atividade")
    fknaturezajuridica: Optional[int] = Field(None, description="FK da natureza jurídica")
    fkporte: Optional[int] = Field(None, description="FK do porte da empresa")
    porteempresa: Optional[int] = Field(None, description="Porte da empresa")
    situacaopessoajuridica: Optional[int] = Field(None, description="Situação da pessoa jurídica")
    
    # Simples Nacional
    simplesnacional: Optional[int] = Field(None, description="Optante pelo Simples Nacional (1=Sim, 0=Não)")
    
    # Contador
    crccontador: Optional[str] = Field(None, max_length=20, description="CRC do contador responsável")
    
    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        return validar_cnpj(v)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo": 2,
                "cnpj": "12.345.678/0001-90",
                "razaosocial": "Empresa Exemplo LTDA",
                "nomefantasia": "Exemplo Corp",
                "inscricaoestadual": "123.456.789.012",
                "cnaefiscal": "6201-5/00",
                "datainicioatividade": "2020-01-15",
                "telefone": "(11) 3456-7890",
                "email": "contato@exemplo.com.br",
                "endereco": "Av. Paulista, 1000",
                "cep": "01310-100",
                "cidade": "São Paulo",
                "simplesnacional": 1,
                "status": 1
            }
        }
    )


class PessoaEstrangeiraCreate(PessoaBase):
    """Schema para criação de Pessoa Estrangeira."""
    
    tipo: int = Field(3, description="Tipo fixo: 3 (Estrangeiro)")
    
    # Identificação estrangeira
    identificacaoestrangeira: str = Field(..., max_length=20, description="Número de identificação estrangeira")
    tipoidentificacaoestrangeira: Optional[str] = Field(None, max_length=30, description="Tipo de identificação (RNE, RNM, etc)")
    
    # Dados pessoais
    datanascimento: Optional[date] = Field(None, description="Data de nascimento")
    nacionalidade: Optional[str] = Field(None, max_length=30, description="Nacionalidade")
    passaporte: Optional[str] = Field(None, max_length=18, description="Número do passaporte")
    datapassaporte: Optional[date] = Field(None, description="Data de emissão do passaporte")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo": 3,
                "identificacaoestrangeira": "RNE123456789",
                "tipoidentificacaoestrangeira": "RNE",
                "nome": "John Smith",
                "nacionalidade": "Estados Unidos",
                "passaporte": "US123456789",
                "telefone": "+1 (555) 123-4567",
                "email": "john.smith@email.com",
                "endereco": "Rua Internacional, 456",
                "status": 1
            }
        }
    )


class PessoaResponse(BaseModel):
    """Schema de resposta para pessoa (todos os tipos)."""
    
    pkpessoa: int
    fkuser: Optional[int] = None
    tipo: int
    status: Optional[int] = None
    
    # Pessoa Física
    cpf: Optional[str] = None
    nome: Optional[str] = None
    datanascimento: Optional[datetime] = None
    naturalidade: Optional[str] = None
    nacionalidade: Optional[str] = None
    estadocivil: Optional[int] = None
    sexo: Optional[int] = None
    rg: Optional[str] = None
    orgaoemissor: Optional[str] = None
    fkestadoemissor: Optional[int] = None
    profissao: Optional[str] = None
    fkprofissao: Optional[int] = None
    filiacaomae: Optional[str] = None
    filiacaopai: Optional[str] = None
    
    # Pessoa Jurídica
    cnpj: Optional[str] = None
    razaosocial: Optional[str] = None
    nomefantasia: Optional[str] = None
    inscricaoestadual: Optional[str] = None
    fkufinscricaoestadual: Optional[int] = None
    inscricaomunicipal: Optional[str] = None
    cnaefiscal: Optional[str] = None
    datainicioatividade: Optional[datetime] = None
    fknaturezajuridica: Optional[int] = None
    fkporte: Optional[int] = None
    porteempresa: Optional[int] = None
    situacaopessoajuridica: Optional[int] = None
    simplesnacional: Optional[int] = None
    crccontador: Optional[str] = None
    
    # Estrangeiro
    passaporte: Optional[str] = None
    datapassaporte: Optional[datetime] = None
    identificacaoestrangeira: Optional[str] = None
    tipoidentificacaoestrangeira: Optional[str] = None
    
    # Contatos
    telefone: Optional[str] = None
    telefonealternativo1: Optional[str] = None
    telefonealternativo2: Optional[str] = None
    email: Optional[str] = None
    emailalternativo: Optional[str] = None
    fax: Optional[str] = None
    faxalternativo: Optional[str] = None
    
    # Endereço
    endereco: Optional[str] = None
    complemento: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    fkmunicipio: Optional[int] = None
    fkestado: Optional[int] = None
    fkpais: Optional[int] = None
    caixapostal: Optional[str] = None
    
    # Metadados
    datacadastro: Optional[datetime] = None
    dataultimaalteracao: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class PessoaUpdateRequest(BaseModel):
    """Schema para atualização de pessoa (campos opcionais)."""
    
    # Campos comuns
    nome: Optional[str] = Field(None, max_length=150)
    status: Optional[int] = None
    
    # Contatos
    telefone: Optional[str] = Field(None, max_length=20)
    telefonealternativo1: Optional[str] = Field(None, max_length=20)
    telefonealternativo2: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    emailalternativo: Optional[EmailStr] = None
    
    # Endereço
    endereco: Optional[str] = Field(None, max_length=800)
    complemento: Optional[str] = Field(None, max_length=80)
    cep: Optional[str] = Field(None, max_length=14)
    cidade: Optional[str] = Field(None, max_length=50)
    fkestado: Optional[int] = None
    fkmunicipio: Optional[int] = None
    
    # Pessoa Física
    rg: Optional[str] = Field(None, max_length=14)
    orgaoemissor: Optional[str] = Field(None, max_length=50)
    profissao: Optional[str] = Field(None, max_length=100)
    
    # Pessoa Jurídica
    nomefantasia: Optional[str] = Field(None, max_length=150)
    inscricaoestadual: Optional[str] = Field(None, max_length=18)
    inscricaomunicipal: Optional[str] = Field(None, max_length=18)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "telefone": "(11) 99999-8888",
                "email": "novo.email@email.com",
                "endereco": "Nova Rua, 999",
                "cep": "98765-432"
            }
        }
    )
