# Implementação da API - Consumo de Água (Etapa 3)

## Resumo da Implementação

Implementação completa da API para a **Etapa 3 - Uso de Água** do formulário de licenciamento ambiental, seguindo o padrão das APIs anteriores (Etapa 1 - Processos e Etapa 2 - Uso de Recursos e Energia).

## Atributos Extraídos da Tela

Com base na análise da tela da Aba 3 - Uso de Água, foram identificados os seguintes campos:

### Origem da Água (Múltipla Seleção)
- Rede Pública
- Poço Artesiano
- Poço Cacimba
- Captação Superficial
- Captação Pluvial
- Caminhão Pipa
- Outro

### Consumo de Água
- Consumo para Uso Humano (m³/dia)
- Consumo para Outros Usos (m³/dia)

### Efluentes
- Volume de Despejo Diário (m³/dia)
- Destino Final do Efluente (campo de seleção)

## Arquivos Criados

### 1. `docs/supabase/f_form_consumo_de_agua.sql`
**Descrição:** Script SQL para criação da tabela no Supabase

**Características:**
- Tabela: `f_form_consumo_de_agua`
- Relacionamento 1:1 com `dados_gerais` via `processo_id`
- Campos booleanos para múltiplas origens de água
- Campos numéricos (numeric 10,2) para volumes de consumo
- Row Level Security (RLS) habilitado
- Política permissiva para usuários autenticados
- Trigger para atualização automática de `updated_at`
- Índice em `processo_id` para performance
- Foreign key com CASCADE para manter integridade referencial

### 2. `app/schemas/consumo_de_agua_schemas.py`
**Descrição:** Schemas Pydantic para validação de dados

**Classes implementadas:**
- `ConsumoDeAguaBase`: Schema base com todos os campos
- `ConsumoDeAguaCreate`: Para criação (inclui processo_id)
- `ConsumoDeAguaUpdate`: Para atualização
- `ConsumoDeAguaResponse`: Para resposta (inclui id, created_at, updated_at)
- `ConsumoDeAguaUpsertRequest`: Para operação de UPSERT

**Validações:**
- Campos numéricos com validação `ge=0` (maior ou igual a zero)
- Uso de `Decimal` para precisão numérica
- Documentação completa com `Field(..., description=...)`
- Exemplos de uso via `json_schema_extra`

### 3. `app/routers/api_v1_consumo_de_agua.py`
**Descrição:** Router FastAPI com endpoints REST

**Endpoints implementados:**

#### POST `/api/v1/consumo-de-agua`
- Cria ou atualiza dados de consumo de água (UPSERT)
- Tenta UPDATE primeiro, se não encontrar faz INSERT
- Retorna: `ConsumoDeAguaResponse` (201 Created)

#### GET `/api/v1/consumo-de-agua/{processo_id}`
- Busca dados por processo_id
- Retorna: `ConsumoDeAguaResponse` (200 OK)
- Retorna: 404 Not Found se não existir

#### DELETE `/api/v1/consumo-de-agua/{processo_id}`
- Remove dados por processo_id
- Retorna: 204 No Content
- Retorna: 404 Not Found se não existir

**Características:**
- Suporte a autenticação JWT via header `Authorization`
- Fallback para admin headers (SERVICE_ROLE) quando não autenticado
- Logging detalhado
- Tratamento de erros consistente
- Validação de Supabase REST habilitado

## Arquivos Alterados

### 1. `main.py`
**Alterações:**
- Importação do novo router `v1_consumo_de_agua_router`
- Registro do router com `app.include_router(v1_consumo_de_agua_router, prefix=settings.API_BASE)`
- Adição de tag metadata para documentação Swagger:
  - Nome: `v1-consumo-de-agua`
  - Descrição com workflow típico
  - Listagem dos endpoints disponíveis

## Padrão de Uniformidade Mantido

A implementação segue rigorosamente o padrão das APIs anteriores:

✅ **Estrutura de arquivos:** Mesma organização (routers/, schemas/, docs/supabase/)  
✅ **Nomenclatura:** Padrão `f_form_*` para tabelas  
✅ **Relacionamentos:** 1:1 com `dados_gerais` via `processo_id`  
✅ **Validação:** Schemas Pydantic com tipos consistentes  
✅ **Segurança:** RLS habilitado, políticas de acesso, JWT  
✅ **Endpoints:** POST (upsert), GET, DELETE  
✅ **Metadados:** `created_at`, `updated_at`, triggers automáticos  
✅ **Documentação:** Swagger com exemplos e descrições  

## Como Utilizar

### 1. Executar o script SQL no Supabase
```sql
-- Executar o arquivo docs/supabase/f_form_consumo_de_agua.sql
-- Isso criará a tabela, índices, triggers e políticas
```

### 2. Testar a API (exemplo com cURL)

```bash
# Criar/Atualizar dados de consumo de água
curl -X POST "http://localhost:8000/api/v1/consumo-de-agua" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_JWT_TOKEN" \
  -d '{
    "processo_id": "PROC-2025-001234",
    "origem_rede_publica": true,
    "origem_poco_artesiano": false,
    "origem_captacao_superficial": true,
    "consumo_uso_humano_m3_dia": 15.5,
    "consumo_outros_usos_m3_dia": 25.0,
    "volume_despejo_diario_m3_dia": 35.0,
    "destino_final_efluente": "Rede de Esgoto Municipal"
  }'

# Consultar dados
curl -X GET "http://localhost:8000/api/v1/consumo-de-agua/PROC-2025-001234" \
  -H "Authorization: Bearer SEU_JWT_TOKEN"

# Deletar dados
curl -X DELETE "http://localhost:8000/api/v1/consumo-de-agua/PROC-2025-001234" \
  -H "Authorization: Bearer SEU_JWT_TOKEN"
```

### 3. Acessar documentação Swagger
```
http://localhost:8000/docs
```

A nova API aparecerá na seção **v1-consumo-de-agua** com todos os endpoints documentados.

## Integração com o Frontend

O frontend deve seguir o mesmo padrão das abas anteriores:

1. Capturar dados do formulário da Aba 3
2. Fazer POST para `/api/v1/consumo-de-agua` com o `processo_id`
3. Tratar resposta (201 Created ou erro)
4. Permitir edição fazendo GET e depois POST novamente (UPSERT)

## Validações de Negócio

A implementação atual contempla validações básicas:
- Campos numéricos devem ser ≥ 0
- Pelo menos uma origem de água deve ser selecionada (validação no frontend)
- Se `volume_despejo_diario_m3_dia` > 0, `destino_final_efluente` deve ser informado (validação no frontend)

---

**Data da Implementação:** 30/10/2025  
**Desenvolvedor:** GitHub Copilot  
**Versão da API:** v1
