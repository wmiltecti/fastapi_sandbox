# 🔍 Verificação: Tabelas Utilizadas pela API v1

## 📊 Tabelas do Supabase

A API v1 de processos (`/api/v1/processos/`) utiliza **2 tabelas principais**:

### 1️⃣ Tabela `processos`
**Endpoint:** `POST /api/v1/processos/`

**Campos:**
- `id` (UUID, auto-gerado)
- `user_id` (TEXT)
- `status` (TEXT, default: "draft")
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Arquivo de referência:** 
- Router: `app/routers/api_v1_processos.py` linha 96
- Path Supabase: `/processos`

---

### 2️⃣ Tabela `dados_gerais`
**Endpoints:** 
- `PUT /api/v1/processos/{processo_id}/dados-gerais` (upsert)

**Campos ORIGINAIS (schema_dados_gerais_supabase.sql):**
- `id` (UUID, PK, auto-gerado)
- `processo_id` (TEXT, UNIQUE)
- `tipo_pessoa` (TEXT)
- `cpf` (TEXT)
- `cnpj` (TEXT)
- `razao_social` (TEXT)
- `nome_fantasia` (TEXT)
- `porte` (TEXT)
- `potencial_poluidor` (TEXT)
- `descricao_resumo` (TEXT)
- `contato_email` (TEXT)
- `contato_telefone` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Campos ADICIONADOS (alteracao_dados_gerais_protocolo.sql):**
- ✅ `protocolo_interno` (TEXT, UNIQUE) - **Gerado automaticamente via trigger**
- ✅ `numero_processo_externo` (TEXT) - Informado pelo usuário
- ✅ `numero_processo_oficial` (TEXT) - Reservado

**Arquivo de referência:**
- Router: `app/routers/api_v1_processos.py` linhas 176 e 186
- Path Supabase UPDATE: `/dados_gerais?processo_id=eq.{processo_id}`
- Path Supabase INSERT: `/dados_gerais`

---

## 🎯 Lógica de Upsert

O endpoint `PUT /dados-gerais` implementa lógica **upsert manual**:

1. **Tenta UPDATE** primeiro:
   ```python
   path=f"/dados_gerais?processo_id=eq.{processo_id}"
   ```
   - Busca registro com `processo_id` igual ao fornecido
   - Se encontrar: atualiza campos (PATCH)

2. **Se UPDATE retornar vazio** (registro não existe):
   ```python
   path="/dados_gerais"
   ```
   - Cria novo registro (POST)
   - **TRIGGER dispara aqui** → gera `protocolo_interno` automaticamente

---

## 🔧 Trigger de Protocolo

**Função:** `gerar_protocolo_interno()`
**Trigger:** `trigger_gerar_protocolo_interno`
**Disparo:** BEFORE INSERT

**Comportamento:**
- Quando um novo registro é inserido em `dados_gerais`
- Se `protocolo_interno` está NULL
- Busca último sequencial do ano atual
- Gera novo protocolo no formato: `YYYY/NNNNNN`
  - Exemplo: `2025/000001`, `2025/000002`...

---

## ✅ Checklist de Verificação no Supabase

Para confirmar que tudo está funcionando:

### 1. Verificar se tabelas existem:
```sql
-- Verificar tabela processos
SELECT * FROM public.processos LIMIT 5;

-- Verificar tabela dados_gerais
SELECT * FROM public.dados_gerais LIMIT 5;
```

### 2. Verificar se migration foi aplicada:
```sql
-- Verificar se colunas de protocolo existem
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'dados_gerais'
AND column_name IN ('protocolo_interno', 'numero_processo_externo', 'numero_processo_oficial');
```

Resultado esperado:
| column_name | data_type | is_nullable |
|------------|-----------|-------------|
| protocolo_interno | text | YES |
| numero_processo_externo | text | YES |
| numero_processo_oficial | text | YES |

### 3. Verificar se trigger existe:
```sql
-- Verificar trigger
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_name = 'trigger_gerar_protocolo_interno';
```

Resultado esperado:
| trigger_name | event_manipulation | event_object_table | action_statement |
|--------------|-------------------|-------------------|------------------|
| trigger_gerar_protocolo_interno | INSERT | dados_gerais | EXECUTE FUNCTION gerar_protocolo_interno() |

### 4. Verificar se função existe:
```sql
-- Verificar função
SELECT 
    proname, 
    prosrc
FROM pg_proc
WHERE proname = 'gerar_protocolo_interno';
```

Deve retornar 1 linha com o nome da função.

### 5. Verificar índices:
```sql
-- Verificar índices
SELECT 
    indexname, 
    indexdef
FROM pg_indexes
WHERE tablename = 'dados_gerais'
AND indexname IN ('idx_dados_gerais_protocolo_interno', 'idx_dados_gerais_numero_externo');
```

---

## 🧪 Teste Manual via API

### Teste 1: Criar processo
```bash
POST http://localhost:8000/api/v1/processos/
Content-Type: application/json

{
  "user_id": "test_user_123",
  "status": "draft"
}
```

**Resposta esperada:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "test_user_123",
  "status": "draft",
  "created_at": "2025-10-28T10:30:00Z",
  "updated_at": "2025-10-28T10:30:00Z"
}
```

**Verificar no Supabase:**
```sql
SELECT * FROM public.processos 
WHERE user_id = 'test_user_123' 
ORDER BY created_at DESC 
LIMIT 1;
```

---

### Teste 2: Criar dados gerais (primeiro registro)
```bash
PUT http://localhost:8000/api/v1/processos/550e8400-e29b-41d4-a716-446655440000/dados-gerais
Content-Type: application/json

{
  "processo_id": "550e8400-e29b-41d4-a716-446655440000",
  "tipo_pessoa": "PJ",
  "cnpj": "12.345.678/0001-90",
  "razao_social": "Empresa Teste LTDA",
  "nome_fantasia": "Teste Corp",
  "porte": "ME",
  "potencial_poluidor": "baixo",
  "contato_email": "teste@exemplo.com",
  "contato_telefone": "(11) 99999-8888",
  "numero_processo_externo": "PROC-2025-001"
}
```

**Resposta esperada:**
```json
{
  "id": "abc-def-123",
  "processo_id": "550e8400-e29b-41d4-a716-446655440000",
  "protocolo_interno": "2025/000001",  // ← GERADO AUTOMATICAMENTE
  "numero_processo_externo": "PROC-2025-001",
  "numero_processo_oficial": null,
  "tipo_pessoa": "PJ",
  "cnpj": "12.345.678/0001-90",
  "razao_social": "Empresa Teste LTDA",
  "nome_fantasia": "Teste Corp",
  "porte": "ME",
  "potencial_poluidor": "baixo",
  "contato_email": "teste@exemplo.com",
  "contato_telefone": "(11) 99999-8888",
  "created_at": "2025-10-28T10:35:00Z",
  "updated_at": "2025-10-28T10:35:00Z"
}
```

**Verificar no Supabase:**
```sql
SELECT 
    protocolo_interno,
    numero_processo_externo,
    razao_social,
    created_at
FROM public.dados_gerais 
WHERE processo_id = '550e8400-e29b-41d4-a716-446655440000';
```

**Resultado esperado:**
| protocolo_interno | numero_processo_externo | razao_social | created_at |
|------------------|------------------------|--------------|------------|
| 2025/000001 | PROC-2025-001 | Empresa Teste LTDA | 2025-10-28 10:35:00 |

---

## 🐛 Troubleshooting

### Problema: Dados não aparecem no Supabase

**Possíveis causas:**

1. **Migration não foi executada**
   - Verificar se colunas `protocolo_interno`, `numero_processo_externo`, `numero_processo_oficial` existem
   - Solução: Executar `alteracao_dados_gerais_protocolo.sql` no SQL Editor do Supabase

2. **Trigger não foi criado**
   - Verificar com query da seção "Verificar se trigger existe"
   - Solução: Executar parte da function + trigger da migration

3. **RLS (Row Level Security) bloqueando visualização**
   - Dados podem estar salvos mas política RLS impede visualização
   - Solução temporária: Desabilitar RLS ou usar SERVICE_ROLE key
   ```sql
   ALTER TABLE dados_gerais DISABLE ROW LEVEL SECURITY;
   ```

4. **Autenticação incorreta**
   - API usando JWT inválido
   - Solução: Verificar logs do Uvicorn para erro 401/403
   - Testar sem Authorization header (usa SERVICE_ROLE automaticamente)

5. **URL do Supabase incorreta**
   - Verificar `SUPABASE_URL` no `.env`
   - Deve ser: `https://[PROJECT_ID].supabase.co`

6. **Chave API incorreta**
   - Verificar `SUPABASE_ANON_KEY` e `SUPABASE_SERVICE_ROLE_KEY`
   - Obter em: Supabase Dashboard → Settings → API

---

## 📝 Logs Úteis

**Verificar logs do Uvicorn:**
```
INFO:httpx:HTTP Request: POST https://xxx.supabase.co/rest/v1//dados_gerais "HTTP/1.1 201 Created"
```

**Status esperados:**
- `201 Created` - INSERT com sucesso
- `200 OK` - UPDATE com sucesso
- `400 Bad Request` - Erro de validação
- `401 Unauthorized` - Token inválido
- `409 Conflict` - Violação de UNIQUE constraint

---

## 🎯 Resumo

✅ **Tabela principal:** `public.dados_gerais`  
✅ **Protocolo gerado:** Via trigger `gerar_protocolo_interno()`  
✅ **Formato:** `YYYY/NNNNNN` (ex: 2025/000001)  
✅ **Endpoints:** POST `/processos` + PUT `/dados-gerais`  

**Se não ver dados:** Execute as queries de verificação acima e confira os logs do Uvicorn.
