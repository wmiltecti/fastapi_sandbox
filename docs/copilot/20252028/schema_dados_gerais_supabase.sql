create table public.dados_gerais (
  id uuid not null default gen_random_uuid (),
  processo_id text not null,
  tipo_pessoa text null,
  cpf text null,
  cnpj text null,
  razao_social text null,
  nome_fantasia text null,
  porte text null,
  potencial_poluidor text null,
  descricao_resumo text null,
  contato_email text null,
  contato_telefone text null,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  constraint dados_gerais_pkey primary key (id),
  constraint dados_gerais_processo_id_key unique (processo_id)
) TABLESPACE pg_default;