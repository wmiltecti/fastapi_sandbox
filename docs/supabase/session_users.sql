-- Criação da tabela de sessões
create table public.session_users (
    id uuid default uuid_generate_v4() primary key,
    cpf varchar not null,
    name varchar not null,
    last_login timestamp with time zone default now(),
    session_token text not null,
    is_active boolean default true
);

-- Índices para performance
create index idx_session_users_cpf on public.session_users(cpf);
create index idx_session_users_token on public.session_users(session_token);

-- Políticas de segurança
create policy "Apenas leitura para sessões ativas"
    on public.session_users
    for select
    using (is_active = true);

create policy "Permite atualização com token válido"
    on public.session_users
    for update
    using (auth.uid() is not null);

-- Habilitar RLS (Row Level Security)
alter table public.session_users enable row level security;