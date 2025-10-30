-- Table: public.f_form_uso_recursos_energia

-- DROP TABLE IF EXISTS public.f_form_uso_recursos_energia;

CREATE TABLE IF NOT EXISTS public.f_form_uso_recursos_energia
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    processo_id text COLLATE pg_catalog."default" NOT NULL,
    
    -- Uso de Lenha
    usa_lenha boolean DEFAULT false,
    quantidade_lenha_m3 numeric(10,2),
    num_ceprof text COLLATE pg_catalog."default",
    
    -- Caldeira
    possui_caldeira boolean DEFAULT false,
    altura_chamine_metros numeric(10,2),
    
    -- Fornos
    possui_fornos boolean DEFAULT false,
    sistema_captacao text COLLATE pg_catalog."default",
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    CONSTRAINT uso_recursos_energia_pkey PRIMARY KEY (id),
    CONSTRAINT uso_recursos_energia_processo_id_key UNIQUE (processo_id),
    CONSTRAINT fk_uso_recursos_energia_processo FOREIGN KEY (processo_id)
        REFERENCES public.dados_gerais (processo_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.f_form_uso_recursos_energia
    OWNER to postgres;

ALTER TABLE IF EXISTS public.f_form_uso_recursos_energia
    ENABLE ROW LEVEL SECURITY;

GRANT ALL ON TABLE public.f_form_uso_recursos_energia TO anon;

GRANT ALL ON TABLE public.f_form_uso_recursos_energia TO authenticated;

GRANT ALL ON TABLE public.f_form_uso_recursos_energia TO postgres;

GRANT ALL ON TABLE public.f_form_uso_recursos_energia TO service_role;

COMMENT ON TABLE public.f_form_uso_recursos_energia
    IS 'Dados da Etapa 2 - Uso de Recursos e Energia do formulário de licenciamento ambiental';

COMMENT ON COLUMN public.f_form_uso_recursos_energia.processo_id
    IS 'Referência ao processo em dados_gerais';

-- Index: idx_uso_recursos_energia_processo_id

-- DROP INDEX IF EXISTS public.idx_uso_recursos_energia_processo_id;

CREATE INDEX IF NOT EXISTS idx_uso_recursos_energia_processo_id
    ON public.f_form_uso_recursos_energia USING btree
    (processo_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- POLICY: Allow all for authenticated users

-- DROP POLICY IF EXISTS "Allow all for authenticated users" ON public.f_form_uso_recursos_energia;

CREATE POLICY "Allow all for authenticated users"
    ON public.f_form_uso_recursos_energia
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (true);

-- Trigger: update_uso_recursos_energia_updated_at

-- DROP TRIGGER IF EXISTS update_uso_recursos_energia_updated_at ON public.f_form_uso_recursos_energia;

CREATE OR REPLACE TRIGGER update_uso_recursos_energia_updated_at
    BEFORE UPDATE
    ON public.f_form_uso_recursos_energia
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();


-- Table: public.f_form_combustiveis_energia

-- DROP TABLE IF EXISTS public.f_form_combustiveis_energia;

CREATE TABLE IF NOT EXISTS public.f_form_combustiveis_energia
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    processo_id text COLLATE pg_catalog."default" NOT NULL,
    tipo_fonte text COLLATE pg_catalog."default" NOT NULL,
    equipamento text COLLATE pg_catalog."default" NOT NULL,
    quantidade numeric(10,2) NOT NULL,
    unidade text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    CONSTRAINT combustiveis_energia_pkey PRIMARY KEY (id),
    CONSTRAINT fk_combustiveis_energia_processo FOREIGN KEY (processo_id)
        REFERENCES public.dados_gerais (processo_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.f_form_combustiveis_energia
    OWNER to postgres;

ALTER TABLE IF EXISTS public.f_form_combustiveis_energia
    ENABLE ROW LEVEL SECURITY;

GRANT ALL ON TABLE public.f_form_combustiveis_energia TO anon;

GRANT ALL ON TABLE public.f_form_combustiveis_energia TO authenticated;

GRANT ALL ON TABLE public.f_form_combustiveis_energia TO postgres;

GRANT ALL ON TABLE public.f_form_combustiveis_energia TO service_role;

COMMENT ON TABLE public.f_form_combustiveis_energia
    IS 'Tabela de combustíveis e energia da Etapa 2 - permite múltiplos registros por processo';

-- Index: idx_combustiveis_energia_processo_id

-- DROP INDEX IF EXISTS public.idx_combustiveis_energia_processo_id;

CREATE INDEX IF NOT EXISTS idx_combustiveis_energia_processo_id
    ON public.f_form_combustiveis_energia USING btree
    (processo_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- POLICY: Allow all for authenticated users

-- DROP POLICY IF EXISTS "Allow all for authenticated users" ON public.f_form_combustiveis_energia;

CREATE POLICY "Allow all for authenticated users"
    ON public.f_form_combustiveis_energia
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (true);

-- Trigger: update_combustiveis_energia_updated_at

-- DROP TRIGGER IF EXISTS update_combustiveis_energia_updated_at ON public.f_form_combustiveis_energia;

CREATE OR REPLACE TRIGGER update_combustiveis_energia_updated_at
    BEFORE UPDATE
    ON public.f_form_combustiveis_energia
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();


-- Função auxiliar para update_updated_at_column (caso não exista)

-- DROP FUNCTION IF EXISTS public.update_updated_at_column();

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';
