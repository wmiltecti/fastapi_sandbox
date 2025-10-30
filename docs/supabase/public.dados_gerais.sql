-- Table: public.dados_gerais

-- DROP TABLE IF EXISTS public.dados_gerais;

CREATE TABLE IF NOT EXISTS public.dados_gerais
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    processo_id text COLLATE pg_catalog."default" NOT NULL,
    tipo_pessoa text COLLATE pg_catalog."default",
    cpf text COLLATE pg_catalog."default",
    cnpj text COLLATE pg_catalog."default",
    razao_social text COLLATE pg_catalog."default",
    nome_fantasia text COLLATE pg_catalog."default",
    porte text COLLATE pg_catalog."default",
    potencial_poluidor text COLLATE pg_catalog."default",
    descricao_resumo text COLLATE pg_catalog."default",
    contato_email text COLLATE pg_catalog."default",
    contato_telefone text COLLATE pg_catalog."default",
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    protocolo_interno text COLLATE pg_catalog."default",
    numero_processo_externo text COLLATE pg_catalog."default",
    numero_processo_oficial text COLLATE pg_catalog."default",
    CONSTRAINT dados_gerais_pkey PRIMARY KEY (id),
    CONSTRAINT dados_gerais_processo_id_key UNIQUE (processo_id),
    CONSTRAINT dados_gerais_protocolo_interno_key UNIQUE (protocolo_interno)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.dados_gerais
    OWNER to postgres;

ALTER TABLE IF EXISTS public.dados_gerais
    ENABLE ROW LEVEL SECURITY;

GRANT ALL ON TABLE public.dados_gerais TO anon;

GRANT ALL ON TABLE public.dados_gerais TO authenticated;

GRANT ALL ON TABLE public.dados_gerais TO postgres;

GRANT ALL ON TABLE public.dados_gerais TO service_role;

COMMENT ON COLUMN public.dados_gerais.protocolo_interno
    IS 'Protocolo gerado automaticamente no formato YYYY/NNNNNN. Único e imutável.';

COMMENT ON COLUMN public.dados_gerais.numero_processo_externo
    IS 'Número do processo informado pelo usuário (opcional). Pode ser alterado.';

COMMENT ON COLUMN public.dados_gerais.numero_processo_oficial
    IS 'Número oficial do processo (a ser definido pela analista). Reservado para uso futuro.';
-- Index: idx_dados_gerais_numero_externo

-- DROP INDEX IF EXISTS public.idx_dados_gerais_numero_externo;

CREATE INDEX IF NOT EXISTS idx_dados_gerais_numero_externo
    ON public.dados_gerais USING btree
    (numero_processo_externo COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_dados_gerais_protocolo_interno

-- DROP INDEX IF EXISTS public.idx_dados_gerais_protocolo_interno;

CREATE INDEX IF NOT EXISTS idx_dados_gerais_protocolo_interno
    ON public.dados_gerais USING btree
    (protocolo_interno COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- POLICY: Allow all for authenticated users

-- DROP POLICY IF EXISTS "Allow all for authenticated users" ON public.dados_gerais;

CREATE POLICY "Allow all for authenticated users"
    ON public.dados_gerais
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (true);

-- Trigger: trigger_gerar_protocolo_interno

-- DROP TRIGGER IF EXISTS trigger_gerar_protocolo_interno ON public.dados_gerais;

CREATE OR REPLACE TRIGGER trigger_gerar_protocolo_interno
    BEFORE INSERT
    ON public.dados_gerais
    FOR EACH ROW
    EXECUTE FUNCTION public.gerar_protocolo_interno();