# Implementação - Etapa 1 do Formulário (Características do Empreendimento)

**Data:** 29/10/2025
**Branch:** `add_api_formulario`
**Desenvolvedor:** GitHub Copilot + wmiltecti

---

## ✅ RESUMO DO TRABALHO REALIZADO

### 1. ANÁLISE E MAPEAMENTO DE CAMPOS

Analisamos a tela da **Etapa 1 de 7** do formulário e identificamos **11 novos campos** que precisavam ser adicionados à tabela `dados_gerais`:

| Campo da Tela | Coluna no Banco | Tipo SQL | Status |
|---------------|-----------------|----------|--------|
| Área Total | `area_total` | `numeric(10,2)` | ✅ NOVO |
| CNAE (código) | `cnae_codigo` | `text` | ✅ NOVO |
| CNAE (descrição) | `cnae_descricao` | `text` | ✅ NOVO |
| Possui Licença Anterior? | `possui_licenca_anterior` | `boolean` | ✅ NOVO |
| Tipo de Licença | `tipo_licenca_anterior` | `text` | ✅ NOVO |
| Número da Licença | `numero_licenca_anterior` | `text` | ✅ NOVO |
| Ano de Emissão | `ano_emissao_licenca` | `integer` | ✅ NOVO |
| Validade | `validade_licenca` | `date` | ✅ NOVO |
| Número de Empregados | `numero_empregados` | `integer` | ✅ NOVO |
| Horário Início | `horario_funcionamento_inicio` | `time` | ✅ NOVO |
| Horário Término | `horario_funcionamento_fim` | `time` | ✅ NOVO |
| Porte do Empreendimento | `porte` | `text` | ⚪ JÁ EXISTIA |
| Potencial Poluidor | `potencial_poluidor` | `text` | ⚪ JÁ EXISTIA |

---

## 2. ARQUIVOS CRIADOS/MODIFICADOS

### 📝 Arquivo CRIADO:
- **`docs/supabase/migration_add_campos_formulario_etapa1.sql`**
  - Script de migração SQL para adicionar novos campos
  - Usa `ADD COLUMN IF NOT EXISTS` (seguro para reexecutar)
  - Inclui comentários em todas as colunas
  - Cria 2 índices para otimização de consultas

### 🔧 Arquivo MODIFICADO:
- **`app/schemas/processo_schemas.py`**
  - Classe `DadosGeraisUpsert`: adicionados 11 novos campos opcionais
  - Classe `DadosGeraisResponse`: adicionados 11 novos campos opcionais
  - Exemplos atualizados com dados da tela do formulário
  - Validações adicionadas (ge=0 para números, ranges para anos)

---

## 3. SCRIPT SQL DE MIGRAÇÃO

**Localização:** `docs/supabase/migration_add_campos_formulario_etapa1.sql`

**Como executar no Supabase:**

1. Acesse: https://supabase.com/dashboard/project/jnhvlqytvssrbwjpolyq/editor
2. Copie o conteúdo do arquivo `migration_add_campos_formulario_etapa1.sql`
3. Cole no SQL Editor
4. Execute (Run)
5. Verifique se todas as colunas foram criadas:
   ```sql
   SELECT column_name, data_type, is_nullable 
   FROM information_schema.columns 
   WHERE table_schema = 'public' AND table_name = 'dados_gerais'
   ORDER BY ordinal_position;
   ```

**Características do script:**
- ✅ Seguro para reexecução (usa `IF NOT EXISTS`)
- ✅ Não altera campos existentes
- ✅ Adiciona comentários descritivos
- ✅ Cria índices: `idx_dados_gerais_cnae_codigo`, `idx_dados_gerais_possui_licenca`

---

## 4. SCHEMAS PYDANTIC ATUALIZADOS

### Classe `DadosGeraisUpsert` (Request)

**Novos campos adicionados:**

```python
# Características do Empreendimento
area_total: Optional[float] = Field(None, ge=0)
cnae_codigo: Optional[str] = None
cnae_descricao: Optional[str] = None

# Licença Anterior
possui_licenca_anterior: Optional[bool] = None
tipo_licenca_anterior: Optional[str] = None
numero_licenca_anterior: Optional[str] = None
ano_emissao_licenca: Optional[int] = Field(None, ge=1900, le=2100)
validade_licenca: Optional[str] = None  # formato: YYYY-MM-DD

# Informações Operacionais
numero_empregados: Optional[int] = Field(None, ge=0)
horario_funcionamento_inicio: Optional[str] = None  # formato: HH:MM
horario_funcionamento_fim: Optional[str] = None  # formato: HH:MM
```

### Classe `DadosGeraisResponse` (Response)

- Mesmos campos adicionados
- Exemplo atualizado com dados realistas da tela

---

## 5. ENDPOINT DA API

**Endpoint existente (não modificado):**

```
PUT /api/v1/processos/{processo_id}/dados-gerais
```

**Exemplo de payload com novos campos:**

```json
{
  "processo_id": "550e8400-e29b-41d4-a716-446655440001",
  "numero_processo_externo": "PROC-2025-002",
  "tipo_pessoa": "PJ",
  "cnpj": "12.345.678/0001-90",
  "razao_social": "Frigorífico Exemplo LTDA",
  "nome_fantasia": "Frigorífico Exemplo",
  "porte": "Médio Porte",
  "potencial_poluidor": "Médio",
  "area_total": 5000.0,
  "cnae_codigo": "1011-2/01",
  "cnae_descricao": "Frigorífico - abate de bovinos",
  "possui_licenca_anterior": true,
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
```

---

## 6. TESTES VIA SWAGGER

**URL Swagger:** http://localhost:8000/docs

### Passo a passo para testar:

1. Abra o Swagger: http://localhost:8000/docs
2. Localize o endpoint: `PUT /api/v1/processos/{processo_id}/dados-gerais`
3. Clique em "Try it out"
4. Preencha:
   - **processo_id:** Use um UUID válido (ex: criar um processo primeiro via `POST /api/v1/processos`)
   - **Request body:** Cole o JSON de exemplo acima
5. Execute
6. Verifique:
   - Status: 200 OK
   - Response inclui todos os campos enviados
   - Campo `protocolo_interno` foi gerado automaticamente
   - Campos `created_at` e `updated_at` foram preenchidos

### Cenários de teste recomendados:

- ✅ **Teste 1:** Criar dados gerais com todos os novos campos preenchidos
- ✅ **Teste 2:** Criar dados gerais com campos novos nulos/omitidos (todos são opcionais)
- ✅ **Teste 3:** Atualizar dados gerais existentes adicionando novos campos
- ✅ **Teste 4:** Verificar validações (ex: `area_total` negativa deve falhar)
- ✅ **Teste 5:** Verificar validações (ex: `ano_emissao_licenca` > 2100 deve falhar)

---

## 7. O QUE NÃO FOI ALTERADO (SISTEMA ESTÁVEL)

✅ **Endpoint:** Lógica do `PUT /{processo_id}/dados-gerais` mantida (upsert manual)
✅ **Campos existentes:** Todos os campos antigos preservados
✅ **Triggers:** `trigger_gerar_protocolo_interno` intacto
✅ **Funções:** `gerar_protocolo_interno()` não alterada
✅ **Políticas RLS:** Row Level Security mantida
✅ **Rotas:** Nenhuma rota alterada
✅ **Middleware:** Sem alterações
✅ **Outros routers:** Não afetados

---

## ❓ DÚVIDAS E DECISÕES PENDENTES

### 1. Unidade de Medida da Área

**Decisão atual:** Área armazenada em **m²** (metros quadrados)

**Questão pendente:** A tela mostra `m²` fixo. Se no futuro precisar suportar outras unidades (hectares, km², etc), será necessário:
- Adicionar coluna `area_unidade` (text)
- Ou criar uma coluna de conversão

**Recomendação:** Manter m² como padrão e converter no front-end se necessário.

---

### 2. Validação de CNAE

**Decisão atual:** CNAE é armazenado como texto livre (código e descrição)

**Questão pendente:** 
- Integrar com base oficial do IBGE para validar CNAEs?
- Criar tabela auxiliar `public.cnae` com códigos válidos?

**Opções:**

**Opção A - Tabela auxiliar local:**
```sql
CREATE TABLE public.cnae (
    codigo text PRIMARY KEY,
    descricao text NOT NULL,
    ativo boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now()
);

-- Foreign key em dados_gerais
ALTER TABLE dados_gerais
ADD CONSTRAINT fk_cnae 
FOREIGN KEY (cnae_codigo) REFERENCES cnae(codigo);
```

**Opção B - Validação via API externa:**
- Integrar com API do IBGE/Receita Federal
- Validar CNAE no momento do cadastro (front-end ou back-end)

**Recomendação atual:** Deixar como texto livre por enquanto e decidir após feedback dos usuários.

---

### 3. Máscara/Formatação de Dados

**Decisão atual:** Dados armazenados "como recebidos" do front-end

**Questão pendente:**
- CPF/CNPJ: armazenar com ou sem formatação?
  - Com máscara: `12.345.678/0001-90`
  - Sem máscara: `12345678000190`

**Recomendação:** 
- Armazenar **sem formatação** (somente números)
- Formatar apenas na exibição (front-end ou serialização)
- Benefícios: facilita buscas, validações e integrações

**Ação futura:** Criar validator Pydantic para limpar máscaras antes de salvar

---

### 4. Validação de Licença Anterior

**Decisão atual:** Campos de licença são todos opcionais

**Questão pendente:** Implementar regra de negócio?

**Regra sugerida:**
```python
# Se possui_licenca_anterior = True, então:
# - tipo_licenca_anterior (obrigatório)
# - numero_licenca_anterior (obrigatório)
# - validade_licenca (obrigatório)
```

**Como implementar:**
- Adicionar validator Pydantic no schema `DadosGeraisUpsert`
- Ou criar constraint no banco:
  ```sql
  ALTER TABLE dados_gerais
  ADD CONSTRAINT check_licenca_completa
  CHECK (
    (possui_licenca_anterior = false) OR
    (possui_licenca_anterior = true AND 
     tipo_licenca_anterior IS NOT NULL AND 
     numero_licenca_anterior IS NOT NULL AND 
     validade_licenca IS NOT NULL)
  );
  ```

**Recomendação:** Implementar no front-end primeiro (validação de formulário) e depois reforçar no back-end.

---

### 5. Validação de Horário de Funcionamento

**Decisão atual:** Horários armazenados como texto (formato HH:MM)

**Questão pendente:** Validar se horário fim > horário início?

**Opção A - Constraint no banco:**
```sql
ALTER TABLE dados_gerais
ADD CONSTRAINT check_horario_valido 
CHECK (horario_funcionamento_fim > horario_funcionamento_inicio);
```

**Opção B - Validator Pydantic:**
```python
from pydantic import model_validator

@model_validator(mode='after')
def check_horario(self):
    if self.horario_funcionamento_inicio and self.horario_funcionamento_fim:
        if self.horario_funcionamento_fim <= self.horario_funcionamento_inicio:
            raise ValueError('Horário de término deve ser posterior ao horário de início')
    return self
```

**Recomendação:** Implementar validator Pydantic para feedback imediato ao usuário.

---

### 6. Validação de Data de Validade da Licença

**Decisão atual:** Data armazenada sem validação de "data futura"

**Questão pendente:** Licença com validade no passado é válida?

**Regra sugerida:**
- Permitir armazenar licenças vencidas (histórico)
- Adicionar campo calculado `licenca_vigente` (boolean) para facilitar consultas
- Ou criar view materializada para licenças ativas

**Recomendação:** Permitir armazenar qualquer data e adicionar campo/flag de status no futuro se necessário.

---

### 7. Tipo de Licença - Enum vs Texto Livre

**Decisão atual:** `tipo_licenca_anterior` é texto livre

**Questão pendente:** Padronizar tipos de licença?

**Tipos comuns:**
- LP - Licença Prévia
- LI - Licença de Instalação
- LO - Licença de Operação
- LAC - Licença Ambiental por Compromisso
- LAR - Licença Ambiental de Regularização

**Opção A - Criar ENUM:**
```sql
CREATE TYPE tipo_licenca_enum AS ENUM ('LP', 'LI', 'LO', 'LAC', 'LAR', 'Outro');

ALTER TABLE dados_gerais
ALTER COLUMN tipo_licenca_anterior TYPE tipo_licenca_enum 
USING tipo_licenca_anterior::tipo_licenca_enum;
```

**Opção B - Manter texto livre:**
- Permite flexibilidade para licenças específicas de estados/municípios
- Mais fácil de adaptar a mudanças legislativas

**Recomendação:** Manter texto livre por enquanto e criar tabela de referência separada se necessário.

---

## 📋 CHECKLIST DE VALIDAÇÃO (PÓS-TESTE)

Após testar no Swagger, verificar:

- [ ] Script SQL executado com sucesso no Supabase
- [ ] Todas as 11 colunas criadas na tabela `dados_gerais`
- [ ] Índices criados (`idx_dados_gerais_cnae_codigo`, `idx_dados_gerais_possui_licenca`)
- [ ] PUT com novos campos retorna status 200
- [ ] Response inclui todos os campos enviados
- [ ] Campos opcionais podem ser omitidos sem erro
- [ ] Validações funcionando (ex: `area_total` negativa falha)
- [ ] Protocolo interno gerado automaticamente
- [ ] Upsert funcionando (update se existe, insert se não existe)
- [ ] Sem erros no console do servidor FastAPI
- [ ] Swagger UI mostra novos campos na documentação

---

## 🚀 PRÓXIMOS PASSOS

1. **Executar script SQL no Supabase** ✅ (aguardando)
2. **Testar via Swagger** ✅ (em andamento)
3. **Validar testes** ⏳ (pendente)
4. **Commit e push:**
   ```powershell
   git add .
   git commit -m "feat: adicionar campos da Etapa 1 do formulário (Características do Empreendimento)"
   git push origin add_api_formulario
   ```
5. **Criar Pull Request** para merge na `master`
6. **Atualizar variáveis de ambiente no Render** (se necessário)
7. **Deploy automático** (após merge)

---

## 📚 REFERÊNCIAS

- **Tabela:** `public.dados_gerais`
- **Endpoint:** `PUT /api/v1/processos/{processo_id}/dados-gerais`
- **Schemas:** `app/schemas/processo_schemas.py`
- **Router:** `app/routers/api_v1_processos.py`
- **Migration:** `docs/supabase/migration_add_campos_formulario_etapa1.sql`

---

## 📝 NOTAS ADICIONAIS

- Todos os novos campos são **opcionais** (`Optional[...]`)
- Compatibilidade retroativa mantida (campos antigos preservados)
- Sistema continua funcionando sem os novos campos
- Front-end pode enviar novos campos gradualmente
- Não há breaking changes na API

---

**Fim do documento**
