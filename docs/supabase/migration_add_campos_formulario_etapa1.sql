-- ============================================================================
-- Migration: Adicionar campos da Etapa 1 do Formulário (Características do Empreendimento)
-- Data: 2025-10-29
-- Descrição: Adiciona campos identificados na tela de formulário à tabela dados_gerais
-- ============================================================================

-- IMPORTANTE: Este script adiciona APENAS os novos campos sem alterar campos existentes

-- 1. Adicionar coluna: Área Total do Empreendimento
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS area_total numeric(10,2);

COMMENT ON COLUMN public.dados_gerais.area_total IS 
'Área total do empreendimento em m² (metros quadrados)';

-- 2. Adicionar colunas: CNAE (Classificação Nacional de Atividades Econômicas)
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS cnae_codigo text;

ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS cnae_descricao text;

COMMENT ON COLUMN public.dados_gerais.cnae_codigo IS 
'Código CNAE do empreendimento (ex: 1011-2/01)';

COMMENT ON COLUMN public.dados_gerais.cnae_descricao IS 
'Descrição da atividade CNAE (ex: Frigorífico - abate de bovinos)';

-- 3. Adicionar colunas: Informações sobre Licença Anterior
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS possui_licenca_anterior boolean DEFAULT false;

ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS tipo_licenca_anterior text;

ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS numero_licenca_anterior text;

ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS ano_emissao_licenca integer;

ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS validade_licenca date;

COMMENT ON COLUMN public.dados_gerais.possui_licenca_anterior IS 
'Indica se o empreendimento possui licença ambiental anterior (Sim/Não)';

COMMENT ON COLUMN public.dados_gerais.tipo_licenca_anterior IS 
'Tipo de licença anterior (ex: LO - Licença de Operação, LP - Licença Prévia, etc)';

COMMENT ON COLUMN public.dados_gerais.numero_licenca_anterior IS 
'Número da licença ambiental anterior (ex: 12345/2023)';

COMMENT ON COLUMN public.dados_gerais.ano_emissao_licenca IS 
'Ano de emissão da licença anterior';

COMMENT ON COLUMN public.dados_gerais.validade_licenca IS 
'Data de validade da licença anterior';

-- 4. Adicionar coluna: Número de Empregados
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS numero_empregados integer;

COMMENT ON COLUMN public.dados_gerais.numero_empregados IS 
'Número total de empregados do empreendimento';

-- 5. Adicionar colunas: Horário de Funcionamento
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS horario_funcionamento_inicio time;

ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS horario_funcionamento_fim time;

COMMENT ON COLUMN public.dados_gerais.horario_funcionamento_inicio IS 
'Horário de início do funcionamento do empreendimento (ex: 07:00)';

COMMENT ON COLUMN public.dados_gerais.horario_funcionamento_fim IS 
'Horário de término do funcionamento do empreendimento (ex: 17:00)';

-- 6. Criar índices para otimizar consultas (opcional, mas recomendado)
CREATE INDEX IF NOT EXISTS idx_dados_gerais_cnae_codigo
    ON public.dados_gerais USING btree (cnae_codigo)
    WHERE cnae_codigo IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_dados_gerais_possui_licenca
    ON public.dados_gerais USING btree (possui_licenca_anterior)
    WHERE possui_licenca_anterior IS NOT NULL;

-- 7. Verificação: Listar todas as colunas da tabela dados_gerais
-- Descomente para executar após a migration:
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_schema = 'public' AND table_name = 'dados_gerais'
-- ORDER BY ordinal_position;

-- ============================================================================
-- FIM DA MIGRATION
-- ============================================================================
