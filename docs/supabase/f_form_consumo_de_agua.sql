-- Table: public.f_form_consumo_de_agua

-- DROP TABLE IF EXISTS public.f_form_consumo_de_agua;

CREATE TABLE IF NOT EXISTS public.f_form_consumo_de_agua
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    processo_id text COLLATE pg_catalog."default" NOT NULL,
    
    -- Origem da Água (campos booleanos para múltipla seleção)
    origem_rede_publica boolean DEFAULT false,
    origem_poco_artesiano boolean DEFAULT false,
    origem_poco_cacimba boolean DEFAULT false,
    origem_captacao_superficial boolean DEFAULT false,
    origem_captacao_pluvial boolean DEFAULT false,
    origem_caminhao_pipa boolean DEFAULT false,
    origem_outro boolean DEFAULT false,
    
    -- Consumo de Água
    consumo_uso_humano_m3_dia numeric(10,2),
    consumo_outros_usos_m3_dia numeric(10,2),
    
    -- Efluentes
    volume_despejo_diario_m3_dia numeric(10,2),
    destino_final_efluente text COLLATE pg_catalog."default",
    
    -- Metadados
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    CONSTRAINT consumo_de_agua_pkey PRIMARY KEY (id),
    CONSTRAINT consumo_de_agua_processo_id_key UNIQUE (processo_id),
    CONSTRAINT fk_consumo_de_agua_processo FOREIGN KEY (processo_id)
        REFERENCES public.dados_gerais (processo_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.f_form_consumo_de_agua
    OWNER to postgres;

ALTER TABLE IF EXISTS public.f_form_consumo_de_agua
    ENABLE ROW LEVEL SECURITY;

GRANT ALL ON TABLE public.f_form_consumo_de_agua TO anon;

GRANT ALL ON TABLE public.f_form_consumo_de_agua TO authenticated;

GRANT ALL ON TABLE public.f_form_consumo_de_agua TO postgres;

GRANT ALL ON TABLE public.f_form_consumo_de_agua TO service_role;

COMMENT ON TABLE public.f_form_consumo_de_agua
    IS 'Dados da Etapa 3 - Uso de Água do formulário de licenciamento ambiental';

COMMENT ON COLUMN public.f_form_consumo_de_agua.processo_id
    IS 'Referência ao processo em dados_gerais';

COMMENT ON COLUMN public.f_form_consumo_de_agua.consumo_uso_humano_m3_dia
    IS 'Consumo de água para uso humano em metros cúbicos por dia';

COMMENT ON COLUMN public.f_form_consumo_de_agua.consumo_outros_usos_m3_dia
    IS 'Consumo de água para outros usos em metros cúbicos por dia';

COMMENT ON COLUMN public.f_form_consumo_de_agua.volume_despejo_diario_m3_dia
    IS 'Volume de despejo diário de efluentes em metros cúbicos por dia';

COMMENT ON COLUMN public.f_form_consumo_de_agua.destino_final_efluente
    IS 'Destino final do efluente (ex: Rede de Esgoto, Fossa Séptica, Curso d''água, etc)';

-- Index: idx_consumo_de_agua_processo_id

-- DROP INDEX IF EXISTS public.idx_consumo_de_agua_processo_id;

CREATE INDEX IF NOT EXISTS idx_consumo_de_agua_processo_id
    ON public.f_form_consumo_de_agua USING btree
    (processo_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- POLICY: Allow all for authenticated users

-- DROP POLICY IF EXISTS "Allow all for authenticated users" ON public.f_form_consumo_de_agua;

CREATE POLICY "Allow all for authenticated users"
    ON public.f_form_consumo_de_agua
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (true);

-- Trigger: update_consumo_de_agua_updated_at

-- DROP TRIGGER IF EXISTS update_consumo_de_agua_updated_at ON public.f_form_consumo_de_agua;

CREATE OR REPLACE TRIGGER update_consumo_de_agua_updated_at
    BEFORE UPDATE 
    ON public.f_form_consumo_de_agua
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();
