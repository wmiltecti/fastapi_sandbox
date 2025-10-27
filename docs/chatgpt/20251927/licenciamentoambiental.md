voltando ao projeto #licenciamentoambiental, lembra do contexto de formulpario que analisamos e criamos um conjunto de prompts para passar para o bolt.new?

Sim, lembro perfeitamente. 💡
Você está se referindo àquele **formulário extenso** (com campos de “dados gerais”, “dados do empreendimento”, “atividade”, “combustível”, etc.) que analisamos para **otimizar a experiência do usuário (UX)** — agrupando campos por contexto e convertendo em um **wizard de múltiplas etapas**, para ser implementado no **Bolt.new** dentro do projeto #licenciamentoambiental.

Na ocasião, estruturamos dois conjuntos principais:

1. ✅ **Checklist de implementação** — com etapas como:

   * Estrutura do wizard (React, etapas dinâmicas, persistência de estado).
   * Agrupamento de campos por contexto (Dados Gerais, Localização, Atividade, Combustível, Responsável Técnico, Documentos).
   * Integração com API (GET/POST `/licenciamento/processo` e `/atividade`).
   * Validação e UX progressiva (auto-salvar, máscaras de CPF/CNPJ, autocompletar, mensagens claras).
   * Revisão final e envio.

2. 💬 **Grupo de Prompts Bolt.new** — prompts prontos para cada fase:

   * **Prompt 1 – Estrutura inicial** (wizard com react-router-dom e tailwind).
   * **Prompt 2 – Dados Gerais** (campos principais, validação, UX).
   * **Prompt 3 – Localização e mapa** (integração com `/geo`, botão “Ver no mapa”).
   * **Prompt 4 – Atividade e parâmetros** (combo CNAE, porte, potencial poluidor).
   * **Prompt 5 – Combustível e energia** (checkbox e condicionais).
   * **Prompt 6 – Responsável técnico e documentos**.
   * **Prompt 7 – Revisão e envio final.**

Posso te recuperar **essa estrutura completa** (checklist + prompts prontos para colar no Bolt.new), atualizada conforme a última versão que você validou com Evelyn.
Quer que eu traga o conjunto inteiro agora — ou apenas o trecho que vai da **etapa “combustível” em diante** (que foi onde paramos)?

ficou ótimo!
Agora, preciso que gere um script para eu rodar no supabase que armazene esses grupos de informações. Qual estratégia sugere para chave primária? E estou analisando os documentos da evelyn para passar mais informações de contexto para voçê.

Perfeito — vamos materializar o “wizard” no banco do Supabase (Postgres) com um esquema limpo, seguro (RLS) e fácil de consumir pela API.

## Estratégia de chave primária

* **UUID v4** via `gen_random_uuid()` (performática, sem coordenação, nativa no Supabase).
* Para um identificador humano e ordenável, criaremos um **protocolo sequencial** (`LCP-AAAA-000001`) gerado por função/sequence — ótimo para o front e para ofícios.

> Por que não `BIGINT` autoincrement? Pode, mas UUID reduz colisão/replicação e é o padrão do Supabase. O **protocolo** cobre a necessidade de ordenação/legibilidade.

---

## Script SQL (cole e execute no Supabase)

```sql
-- =========================================================
-- 1) Extensões e Schema
-- =========================================================
create schema if not exists licenciamento;

-- gen_random_uuid() vem do pgcrypto; no Supabase geralmente já está ativo.
create extension if not exists pgcrypto;

-- PostGIS é opcional; habilite se quiser armazenar geometria (p.ex. ponto)
create extension if not exists postgis;

-- =========================================================
-- 2) Sequence + Função para gerar PROTOCOLO humano-legível
--     Formato: LCP-YYYY-000001
-- =========================================================
create sequence if not exists licenciamento.protocolo_seq;

create or replace function licenciamento.make_protocolo()
returns text
language plpgsql
as $$
declare
  y text := to_char(now(), 'YYYY');
  n bigint;
begin
  n := nextval('licenciamento.protocolo_seq');
  return 'LCP-' || y || '-' || lpad(n::text, 6, '0');
end;
$$;

-- =========================================================
-- 3) Função utilitária para updated_at
-- =========================================================
create or replace function licenciamento.tg_set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

-- =========================================================
-- 4) Tabela principal do processo (1 por wizard)
-- =========================================================
create table if not exists licenciamento.processo (
  id uuid primary key default gen_random_uuid(),
  protocolo text not null unique default licenciamento.make_protocolo(),
  status text not null default 'draft'
    check (status in ('draft','in_review','submitted','approved','rejected')),
  user_id uuid not null references auth.users(id) on delete restrict,

  -- relacionamento eventual com o legado/espelho (opcional)
  pessoa_id_legacy bigint,       -- se espelhar f_pessoa
  imovel_id_legacy bigint,       -- se espelhar f_imovel

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_processo_user on licenciamento.processo(user_id);

create trigger tg_processo_updated
before update on licenciamento.processo
for each row execute function licenciamento.tg_set_updated_at();

-- =========================================================
-- 5) DADOS GERAIS (1:1 com processo)
-- =========================================================
create table if not exists licenciamento.processo_dados_gerais (
  processo_id uuid primary key references licenciamento.processo(id) on delete cascade,

  -- identificação do requerente/empresa
  tipo_pessoa text check (tipo_pessoa in ('PF','PJ')),
  cpf varchar(14),
  cnpj varchar(18),
  razao_social text,
  nome_fantasia text,

  -- classificação da atividade (parâmetros de negócio)
  porte text,                    -- Pequeno, Médio, Grande, Excepcional
  potencial_poluidor text,       -- Baixo, Médio, Alto
  descricao_resumo text,

  contato_email text,
  contato_telefone text,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger tg_dados_gerais_updated
before update on licenciamento.processo_dados_gerais
for each row execute function licenciamento.tg_set_updated_at();

-- =========================================================
-- 6) LOCALIZAÇÃO (N:1 com processo) – suporta múltiplos pontos/endereços
--     Armazena lat/lon e opcionalmente geometria Point SIRGAS 4674
-- =========================================================
create table if not exists licenciamento.processo_localizacao (
  id uuid primary key default gen_random_uuid(),
  processo_id uuid not null references licenciamento.processo(id) on delete cascade,

  endereco text,
  numero text,
  bairro text,
  municipio_ibge varchar(7),  -- ex: 1100205
  uf char(2),
  cep varchar(15),

  latitude numeric(9,6),
  longitude numeric(9,6),
  geom geometry(Point, 4674),

  referencia text,            -- ponto de referência / observações

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_loc_processo on licenciamento.processo_localizacao(processo_id);
create index if not exists idx_loc_municipio on licenciamento.processo_localizacao(municipio_ibge);
create index if not exists idx_loc_geom on licenciamento.processo_localizacao using gist(geom);

create trigger tg_localizacao_updated
before update on licenciamento.processo_localizacao
for each row execute function licenciamento.tg_set_updated_at();

-- =========================================================
-- 7) ATIVIDADE (N:1) – suporta múltiplas atividades/capacidades
--     Integra com CNAE e parâmetros de porte/potencial
-- =========================================================
create table if not exists licenciamento.processo_atividade (
  id uuid primary key default gen_random_uuid(),
  processo_id uuid not null references licenciamento.processo(id) on delete cascade,

  cnae text,                  -- ex: 35.11-5-00
  atividade_codigo text,      -- código interno/legado se houver
  atividade_nome text,

  unidade_medida text,        -- ex: "m³/dia", "t/ano"
  capacidade_prevista numeric(18,4),

  observacoes text,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_atividade_processo on licenciamento.processo_atividade(processo_id);
create index if not exists idx_atividade_cnae on licenciamento.processo_atividade(cnae);

create trigger tg_atividade_updated
before update on licenciamento.processo_atividade
for each row execute function licenciamento.tg_set_updated_at();

-- =========================================================
-- 8) COMBUSTÍVEL (N:1) – etapa “Combustível e energia”
-- =========================================================
create table if not exists licenciamento.processo_combustivel (
  id uuid primary key default gen_random_uuid(),
  processo_id uuid not null references licenciamento.processo(id) on delete cascade,

  tipo text not null,                     -- ex: Diesel, Gasolina, GLP, Lenha, Etanol
  consumo_mensal numeric(18,4),           -- valor
  consumo_unidade text,                   -- ex: L, kg, m³

  armazenamento_tipo text,                -- TQ aéreo, TQ enterrado, Cilindro, etc.
  capacidade_armazenamento numeric(18,4),
  possui_sistema_contencao boolean,       -- bacia de contenção, etc.

  risco_classificacao text,               -- se aplicável (ex: NR-20)
  observacoes text,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_comb_processo on licenciamento.processo_combustivel(processo_id);
create index if not exists idx_comb_tipo on licenciamento.processo_combustivel(tipo);

create trigger tg_combustivel_updated
before update on licenciamento.processo_combustivel
for each row execute function licenciamento.tg_set_updated_at();

-- =========================================================
-- 9) ENERGIA (N:1) – fontes e demanda
-- =========================================================
create table if not exists licenciamento.processo_energia (
  id uuid primary key default gen_random_uuid(),
  processo_id uuid not null references licenciamento.processo(id) on delete cascade,

  fonte text not null,                    -- Rede, Solar, Biomassa, Gerador, PCH etc.
  demanda_kwh_mensal numeric(18,2),

  possui_gerador boolean default false,
  gerador_potencia_kva numeric(18,2),
  gerador_combustivel text,               -- Diesel, Gás, etc.

  observacoes text,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_energia_processo on licenciamento.processo_energia(processo_id);

create trigger tg_energia_updated
before update on licenciamento.processo_energia
for each row execute function licenciamento.tg_set_updated_at();

-- =========================================================
-- 10) RESPONSÁVEL TÉCNICO (1:1) – se houver 1 por processo
--     Se precisar N:1, remova a unique constraint do processo_id.
-- =========================================================
create table if not exists licenciamento.processo_responsavel_tecnico (
  id uuid primary key default gen_random_uuid(),
  processo_id uuid not null unique references licenciamento.processo(id) on delete cascade,

  -- ligação opcional com pessoa do legado
  pessoa_id_legacy bigint,

  nome text not null,
  cpf varchar(14),
  conselho text,           -- CREA/CRBio/CRQ...
  registro text,           -- nº do registro no conselho
  email text,
  telefone text,

  art_numero text,         -- se aplicável
  art_data date,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger tg_resptec_updated
before update on licenciamento.processo_responsavel_tecnico
for each row execute function licenciamento.tg_set_updated_at();

-- =========================================================
-- 11) DOCUMENTOS (N:1) – referenciando arquivos no Storage do Supabase
-- =========================================================
create table if not exists licenciamento.processo_documento (
  id uuid primary key default gen_random_uuid(),
  processo_id uuid not null references licenciamento.processo(id) on delete cascade,

  tipo text not null,            -- ex: "Requerimento", "Memorial", "Licença Anterior"
  nome_arquivo text not null,
  storage_path text not null,    -- ex: bucket/key.ext
  tamanho_bytes bigint,
  hash_sha256 text,              -- integridade/contador de versão

  uploaded_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create index if not exists idx_doc_processo on licenciamento.processo_documento(processo_id);
create index if not exists idx_doc_tipo on licenciamento.processo_documento(tipo);

-- =========================================================
-- 12) RLS – Políticas de segurança por proprietário (user_id)
--      A API do Supabase vai respeitar essas regras automaticamente.
-- =========================================================
alter table licenciamento.processo enable row level security;
alter table licenciamento.processo_dados_gerais enable row level security;
alter table licenciamento.processo_localizacao enable row level security;
alter table licenciamento.processo_atividade enable row level security;
alter table licenciamento.processo_combustivel enable row level security;
alter table licenciamento.processo_energia enable row level security;
alter table licenciamento.processo_responsavel_tecnico enable row level security;
alter table licenciamento.processo_documento enable row level security;

-- Dono pode ler seu próprio processo
create policy p_processo_select_owner
  on licenciamento.processo
  for select
  using (auth.uid() = user_id);

-- Dono pode inserir processo vinculando a si mesmo
create policy p_processo_insert_owner
  on licenciamento.processo
  for insert
  with check (auth.uid() = user_id);

-- Dono pode atualizar/excluir
create policy p_processo_update_owner
  on licenciamento.processo
  for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy p_processo_delete_owner
  on licenciamento.processo
  for delete
  using (auth.uid() = user_id);

-- Para tabelas filhas, a regra checa o dono via join no processo
create policy p_child_select_owner on licenciamento.processo_dados_gerais
  for select using (exists (
    select 1 from licenciamento.processo p
    where p.id = processo_id and p.user_id = auth.uid()
  ));
create policy p_child_ins_owner on licenciamento.processo_dados_gerais
  for insert with check (exists (
    select 1 from licenciamento.processo p
    where p.id = processo_id and p.user_id = auth.uid()
  ));
create policy p_child_upd_owner on licenciamento.processo_dados_gerais
  for update using (exists (
    select 1 from licenciamento.processo p
    where p.id = processo_id and p.user_id = auth.uid()
  )) with check (exists (
    select 1 from licenciamento.processo p
    where p.id = processo_id and p.user_id = auth.uid()
  ));
create policy p_child_del_owner on licenciamento.processo_dados_gerais
  for delete using (exists (
    select 1 from licenciamento.processo p
    where p.id = processo_id and p.user_id = auth.uid()
  ));

-- Replique as 4 políticas child para cada tabela filha:
do $$
declare t text;
begin
  for t in
    select unnest(array[
      'processo_localizacao',
      'processo_atividade',
      'processo_combustivel',
      'processo_energia',
      'processo_responsavel_tecnico',
      'processo_documento'
    ])
  loop
    execute format($SQL$
      create policy p_%1$s_select_owner on licenciamento.%1$s
        for select using (exists (
          select 1 from licenciamento.processo p
          where p.id = processo_id and p.user_id = auth.uid()
        ));
    $SQL$, t);

    execute format($SQL$
      create policy p_%1$s_insert_owner on licenciamento.%1$s
        for insert with check (exists (
          select 1 from licenciamento.processo p
          where p.id = processo_id and p.user_id = auth.uid()
        ));
    $SQL$, t);

    execute format($SQL$
      create policy p_%1$s_update_owner on licenciamento.%1$s
        for update using (exists (
          select 1 from licenciamento.processo p
          where p.id = processo_id and p.user_id = auth.uid()
        )) with check (exists (
          select 1 from licenciamento.processo p
          where p.id = processo_id and p.user_id = auth.uid()
        ));
    $SQL$, t);

    execute format($SQL$
      create policy p_%1$s_delete_owner on licenciamento.%1$s
        for delete using (exists (
          select 1 from licenciamento.processo p
          where p.id = processo_id and p.user_id = auth.uid()
        ));
    $SQL$, t);
  end loop;
end$$;

-- =========================================================
-- 13) Views úteis (ex.: status do preenchimento do wizard)
-- =========================================================
create or replace view licenciamento.processo_wizard_status as
select
  p.id,
  p.protocolo,
  p.status,
  (select exists (select 1 from licenciamento.processo_dados_gerais d where d.processo_id = p.id)) as v_dados_gerais,
  (select count(*) from licenciamento.processo_localizacao l where l.processo_id = p.id)       as n_localizacoes,
  (select count(*) from licenciamento.processo_atividade a  where a.processo_id = p.id)       as n_atividades,
  (select count(*) from licenciamento.processo_combustivel c where c.processo_id = p.id)      as n_combustiveis,
  (select count(*) from licenciamento.processo_energia e     where e.processo_id = p.id)      as n_energias,
  (select exists (select 1 from licenciamento.processo_responsavel_tecnico r where r.processo_id = p.id)) as v_resp_tecnico,
  (select count(*) from licenciamento.processo_documento d    where d.processo_id = p.id)     as n_documentos,
  p.created_at, p.updated_at, p.user_id
from licenciamento.processo p;

-- Opcionalmente, RLS da view (Postgres herda das tabelas).
-- Você também pode criar uma policy específica para SELECT na view via segurança de tabela, se preferir materializar.

-- =========================================================
-- 14) Índices adicionais opcionais
-- =========================================================
-- Se uso frequente de buscas por protocolo:
create index if not exists idx_processo_protocolo on licenciamento.processo(protocolo);
```

---

## Notas rápidas para a API

* Endpoints típicos (REST):

  * `POST /processos` → cria `licenciamento.processo` (front envia `user_id` via JWT automaticamente no Supabase).
  * `PUT /processos/:id` → atualiza `status`.
  * `PUT /processos/:id/dados-gerais` → upsert 1:1.
  * `POST /processos/:id/localizacoes` / `atividades` / `combustiveis` / `energia` / `documentos`.
  * `GET /processos/:id/wizard-status` → usa a `view` para montar o progresso.

* O `protocolo` evita expor o UUID no front público e facilita atendimento.

---

Se quiser, eu já **preparo os `INSERT/UPSERT` SQL/JSON** de exemplo (com os mesmos nomes de campos que usamos nos prompts do Bolt.new) para você testar no **SQL Editor** do Supabase — e também deixo um **script de migração** para absorver códigos/valores que a Evelyn padronizou (listas de combustíveis, fontes de energia, regras de validação por porte/potencial). Quer que eu inclua esses *seeds* agora?

sim, por favor! a ideia é não conectar direto ao banco, fazer toda a parte de crud via api.


perfeito! vamos manter **tudo via API (PostgREST + Storage)**. abaixo deixo:

1. **pré-requisitos rápidos**
2. **endpoints e exemplos (curl/axios)** para cada etapa do wizard
3. **upsert idempotente** (sem risco de duplicar)
4. **seeds de listas (combustível, fonte de energia, porte, potencial)** – via API
5. **upload de documento** (Storage) + registro na tabela

> Observação: o DDL das tabelas do meu passo anterior já cobre o CRUD. Aqui usamos **/rest/v1** do Supabase e **Storage** — sem conexão direta ao banco.

---

# 1) Pré-requisitos (uma vez)

* Base URL REST do projeto: `https://<PROJECT_REF>.supabase.co/rest/v1`
* Header **Auth**:

  * Para **usuário** logado no front: `Authorization: Bearer <JWT do usuário>` (RLS valida `auth.uid()`).
  * Para **seed/administrativo** (servidor/CLI): `apikey: <SERVICE_ROLE>` e `Authorization: Bearer <SERVICE_ROLE>`.
* Incluir sempre:

  * `Content-Type: application/json`
  * `Accept: application/json`
  * `Prefer: return=representation`

> Os exemplos abaixo usam placeholders: `<PROJECT_REF>`, `<ANON_OR_SERVICE_KEY>`, `<USER_JWT>`.

---

# 2) CRUD do Wizard — exemplos via API

## 2.1 Criar processo (gera `protocolo` automático)

**POST** `/rest/v1/licenciamento.processo`

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' \
  -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation' \
  -d '{
    "user_id": "<USER_UUID>",
    "status": "draft"
  }'
```

**Resposta** (resumo): `[{ "id": "...uuid...", "protocolo": "LCP-2025-000123", ... }]`

---

## 2.2 Upsert **Dados Gerais** (1:1 por processo)

**POST** com upsert em `processo_id`:
**on_conflict=processo_id + Prefer: resolution=merge-duplicates**

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_dados_gerais?on_conflict=processo_id' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' \
  -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation, resolution=merge-duplicates' \
  -d '{
    "processo_id": "<PROCESSO_UUID>",
    "tipo_pessoa": "PJ",
    "cnpj": "12.345.678/0001-90",
    "razao_social": "Empresa Exemplo SA",
    "nome_fantasia": "Exemplo",
    "porte": "Médio",
    "potencial_poluidor": "Alto",
    "descricao_resumo": "Implantação de unidade industrial.",
    "contato_email": "contato@exemplo.com",
    "contato_telefone": "(69) 99999-0000"
  }'
```

---

## 2.3 **Localização** (N:1)

**POST** `/rest/v1/licenciamento.processo_localizacao`

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_localizacao' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation' \
  -d '{
    "processo_id": "<PROCESSO_UUID>",
    "endereco": "Rod. BR-364, km 10",
    "municipio_ibge": "1100205",
    "uf": "RO",
    "cep": "76800-000",
    "latitude": -8.759321,
    "longitude": -63.903112,
    "referencia": "Próximo ao posto X"
  }'
```

> Se quiser geom mais tarde, podemos criar trigger para construir `geom` a partir de lat/long — mantendo o CRUD igual.

---

## 2.4 **Atividade** (N:1)

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_atividade' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation' \
  -d '{
    "processo_id": "<PROCESSO_UUID>",
    "cnae": "35.11-5-00",
    "atividade_codigo": "INT-ENERGIA-001",
    "atividade_nome": "Geração de energia termoelétrica",
    "unidade_medida": "MWh/mês",
    "capacidade_prevista": 2400,
    "observacoes": "Operação em dois turnos."
  }'
```

---

## 2.5 **Combustível** (N:1)

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_combustivel' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation' \
  -d '{
    "processo_id": "<PROCESSO_UUID>",
    "tipo": "Diesel",
    "consumo_mensal": 12000,
    "consumo_unidade": "L",
    "armazenamento_tipo": "Tanque aéreo",
    "capacidade_armazenamento": 30000,
    "possui_sistema_contencao": true,
    "risco_classificacao": "NR-20 Classe II",
    "observacoes": "Tanque com bacia de contenção certificada."
  }'
```

---

## 2.6 **Energia** (N:1)

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_energia' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation' \
  -d '{
    "processo_id": "<PROCESSO_UUID>",
    "fonte": "Rede",
    "demanda_kwh_mensal": 180000,
    "possui_gerador": true,
    "gerador_potencia_kva": 500,
    "gerador_combustivel": "Diesel",
    "observacoes": "Gerador para contingência."
  }'
```

---

## 2.7 **Responsável Técnico** (1:1)

Upsert pelo `processo_id` (unique):

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_responsavel_tecnico?on_conflict=processo_id' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation, resolution=merge-duplicates' \
  -d '{
    "processo_id": "<PROCESSO_UUID>",
    "nome": "Maria Souza",
    "cpf": "123.456.789-00",
    "conselho": "CREA",
    "registro": "RO-123456",
    "email": "maria.souza@exemplo.com",
    "telefone": "(69) 98888-7777",
    "art_numero": "ART-2025-001",
    "art_data": "2025-10-10"
  }'
```

---

## 2.8 **Status do wizard** (View)

```bash
curl -X GET \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_wizard_status?id=eq.<PROCESSO_UUID>' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' \
  -H 'apikey: <ANON_OR_SERVICE_KEY>'
```

---

## 2.9 **Transição de status** (ex.: enviar para revisão)

```bash
curl -X PATCH \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo?id=eq.<PROCESSO_UUID>' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -d '{ "status": "in_review" }'
```

---

# 3) Idempotência / Upsert seguro

* **1:1** (`dados_gerais`, `responsavel_tecnico`): use `?on_conflict=processo_id` + header `Prefer: resolution=merge-duplicates`.
* **N:1** (listas): para evitar duplicação, defina **chave natural** (ex.: `unique(processo_id, tipo)` para combustível). Se quiser, eu te mando o ALTER para criar esses `unique` auxiliares.

---

# 4) Seeds de listas — via API (sem mexer no DB direto)

> Se você **não** criou tabelas de referência (ref_*), pode semear como **arrays do front**.
> Se **preferir persistir** listas para uso por API, crie duas tabelinhas simples (uma vez, no SQL editor) e **popule via REST**:

### (opcional, uma vez) DDL das listas

```sql
create table if not exists licenciamento.ref_combustivel (
  id uuid primary key default gen_random_uuid(),
  nome text unique not null,
  ativo boolean default true
);
create table if not exists licenciamento.ref_energia_fonte (
  id uuid primary key default gen_random_uuid(),
  nome text unique not null,
  ativo boolean default true
);
create table if not exists licenciamento.ref_classificacao (
  id uuid primary key default gen_random_uuid(),
  tipo text not null check (tipo in ('porte','potencial_poluidor')),
  nome text not null,
  unique (tipo, nome)
);
alter table licenciamento.ref_combustivel enable row level security;
alter table licenciamento.ref_energia_fonte enable row level security;
alter table licenciamento.ref_classificacao enable row level security;

-- políticas simples: leitura pública autenticada
create policy r_all_ref_comb on licenciamento.ref_combustivel for select using (true);
create policy r_all_ref_energia on licenciamento.ref_energia_fonte for select using (true);
create policy r_all_ref_class on licenciamento.ref_classificacao for select using (true);

-- escrita: apenas service role (para seed)
create policy w_srv_ref_comb on licenciamento.ref_combustivel for insert to service_role with check (true);
create policy w_srv_ref_energia on licenciamento.ref_energia_fonte for insert to service_role with check (true);
create policy w_srv_ref_class on licenciamento.ref_classificacao for insert to service_role with check (true);
```

### Inserir **seeds** via REST (use **SERVICE ROLE**)

**Combustíveis**

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.ref_combustivel' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <SERVICE_ROLE>' -H 'apikey: <SERVICE_ROLE>' \
  -H 'Prefer: return=representation' \
  -d '[
    {"nome":"Diesel"},{"nome":"Gasolina"},{"nome":"GLP"},
    {"nome":"Lenha"},{"nome":"Etanol"},{"nome":"Gás Natural"}
  ]'
```

**Fontes de energia**

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.ref_energia_fonte' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <SERVICE_ROLE>' -H 'apikey: <SERVICE_ROLE>' \
  -H 'Prefer: return=representation' \
  -d '[
    {"nome":"Rede"},{"nome":"Solar"},{"nome":"Eólica"},
    {"nome":"Biomassa"},{"nome":"PCH"},{"nome":"Gerador"}
  ]'
```

**Classificações (porte / potencial)**

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.ref_classificacao' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <SERVICE_ROLE>' -H 'apikey: <SERVICE_ROLE>' \
  -H 'Prefer: return=representation' \
  -d '[
    {"tipo":"porte","nome":"Pequeno"},
    {"tipo":"porte","nome":"Médio"},
    {"tipo":"porte","nome":"Grande"},
    {"tipo":"porte","nome":"Excepcional"},
    {"tipo":"potencial_poluidor","nome":"Baixo"},
    {"tipo":"potencial_poluidor","nome":"Médio"},
    {"tipo":"potencial_poluidor","nome":"Alto"}
  ]'
```

> No front (Bolt.new), você consome via `GET /rest/v1/licenciamento.ref_*?select=*` para preencher combos.

---

# 5) Upload de **Documento** (Storage) + registro

## 5.1 Enviar arquivo ao **Storage**

Crie um bucket (ex.: `licenciamento-docs`) com política de acesso adequada (privado). Depois, faça upload:

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/storage/v1/object/licenciamento-docs/<PROCESSO_UUID>/requerimento.pdf' \
  -H 'Authorization: Bearer <USER_JWT>' \
  -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Content-Type: application/pdf' \
  --data-binary '@./requerimento.pdf'
```

A resposta trará `Key` (ex.: `licenciamento-docs/<PROCESSO_UUID>/requerimento.pdf`).

## 5.2 Registrar metadados na tabela

```bash
curl -X POST \
  'https://<PROJECT_REF>.supabase.co/rest/v1/licenciamento.processo_documento' \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -H 'Authorization: Bearer <USER_JWT>' -H 'apikey: <ANON_OR_SERVICE_KEY>' \
  -H 'Prefer: return=representation' \
  -d '{
    "processo_id": "<PROCESSO_UUID>",
    "tipo": "Requerimento",
    "nome_arquivo": "requerimento.pdf",
    "storage_path": "licenciamento-docs/<PROCESSO_UUID>/requerimento.pdf",
    "tamanho_bytes": 2345678,
    "hash_sha256": "c0ffeebabe...opcional"
  }'
```

---

# 6) Snippets prontos (Bolt.new)

## 6.1 Axios client

```ts
// src/services/http.ts
import axios from "axios";

export const api = axios.create({
  baseURL: "https://<PROJECT_REF>.supabase.co/rest/v1",
  headers: {
    apikey: import.meta.env.VITE_SUPABASE_ANON_KEY!,
    Authorization: `Bearer ${localStorage.getItem("supabase_jwt") || ""}`,
    Accept: "application/json",
    "Content-Type": "application/json",
    Prefer: "return=representation",
  },
});
```

## 6.2 Criar processo

```ts
export async function createProcess(userId: string) {
  const { data } = await api.post("/licenciamento.processo", {
    user_id: userId,
    status: "draft",
  });
  return data[0]; // { id, protocolo, ... }
}
```

## 6.3 Upsert dados gerais

```ts
export async function upsertDadosGerais(payload: any) {
  const { data } = await api.post(
    "/licenciamento.processo_dos_gerais?on_conflict=processo_id",
    payload,
    { headers: { Prefer: "return=representation, resolution=merge-duplicates" } }
  );
  return data[0];
}
```

> ajuste o endpoint para `processo_dados_gerais` (sem o typo) ao colar.

---

# 7) Quer que eu já deixe:

* os **ALTER TABLE UNIQUE** de “combustível por tipo” e “energia por fonte” para bloquear duplicatas por processo?
* uma **Edge Function** `POST /processos/:id/submit` que faça validações finais (ex.: exige pelo menos 1 localização, 1 atividade e responsável técnico) antes de trocar `status → in_review`?

Se você me der o **mapa de regras** dos documentos da Evelyn (por porte/potencial/atividade), já devolvo a **validação server-side** pronta (procedures ou Edge Function) e os **prompts do Bolt.new** para consumir esses endpoints.

