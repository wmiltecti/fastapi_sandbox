-- Alteração da tabela dados_gerais para suportar protocolos
-- Data: 2025-10-28
-- Objetivo: Adicionar campos para identificação única de processos

-- 1. Adicionar campo para protocolo interno (gerado automaticamente)
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS protocolo_interno TEXT UNIQUE;

-- 2. Adicionar campo para protocolo/número externo (informado pelo usuário)
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS numero_processo_externo TEXT;

-- 3. Adicionar campo reserva para número oficial (aguardando definição da analista)
ALTER TABLE public.dados_gerais
ADD COLUMN IF NOT EXISTS numero_processo_oficial TEXT;

-- 4. Criar índice para melhorar performance de busca por protocolo interno
CREATE INDEX IF NOT EXISTS idx_dados_gerais_protocolo_interno 
ON public.dados_gerais(protocolo_interno);

-- 5. Criar índice para número externo
CREATE INDEX IF NOT EXISTS idx_dados_gerais_numero_externo 
ON public.dados_gerais(numero_processo_externo);

-- 6. Criar função para gerar protocolo interno automaticamente
CREATE OR REPLACE FUNCTION gerar_protocolo_interno()
RETURNS TRIGGER AS $$
DECLARE
    ano_atual TEXT;
    sequencial INT;
    novo_protocolo TEXT;
BEGIN
    -- Se protocolo_interno já está definido, não faz nada
    IF NEW.protocolo_interno IS NOT NULL THEN
        RETURN NEW;
    END IF;

    -- Obtém o ano atual
    ano_atual := TO_CHAR(CURRENT_DATE, 'YYYY');

    -- Busca o último sequencial do ano
    SELECT COALESCE(MAX(
        CAST(
            SPLIT_PART(protocolo_interno, '/', 2) AS INTEGER
        )
    ), 0) INTO sequencial
    FROM public.dados_gerais
    WHERE protocolo_interno LIKE ano_atual || '/%';

    -- Incrementa o sequencial
    sequencial := sequencial + 1;

    -- Gera o novo protocolo no formato YYYY/NNNNNN (ex: 2025/000001)
    novo_protocolo := ano_atual || '/' || LPAD(sequencial::TEXT, 6, '0');

    -- Atribui o novo protocolo
    NEW.protocolo_interno := novo_protocolo;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. Criar trigger para gerar protocolo automaticamente no INSERT
DROP TRIGGER IF EXISTS trigger_gerar_protocolo_interno ON public.dados_gerais;
CREATE TRIGGER trigger_gerar_protocolo_interno
    BEFORE INSERT ON public.dados_gerais
    FOR EACH ROW
    EXECUTE FUNCTION gerar_protocolo_interno();

-- 8. Comentários explicativos
COMMENT ON COLUMN public.dados_gerais.protocolo_interno IS 
'Protocolo gerado automaticamente no formato YYYY/NNNNNN. Único e imutável.';

COMMENT ON COLUMN public.dados_gerais.numero_processo_externo IS 
'Número do processo informado pelo usuário (opcional). Pode ser alterado.';

COMMENT ON COLUMN public.dados_gerais.numero_processo_oficial IS 
'Número oficial do processo (a ser definido pela analista). Reservado para uso futuro.';

-- 9. Atualizar registros existentes (se houver)
-- Gera protocolos retroativos para registros que não têm
DO $$
DECLARE
    registro RECORD;
    contador INT := 1;
    ano_atual TEXT := TO_CHAR(CURRENT_DATE, 'YYYY');
BEGIN
    FOR registro IN 
        SELECT id FROM public.dados_gerais 
        WHERE protocolo_interno IS NULL
        ORDER BY created_at
    LOOP
        UPDATE public.dados_gerais
        SET protocolo_interno = ano_atual || '/' || LPAD(contador::TEXT, 6, '0')
        WHERE id = registro.id;
        
        contador := contador + 1;
    END LOOP;
END $$;

-- Resultado esperado:
-- ✅ protocolo_interno: gerado automaticamente (2025/000001, 2025/000002...)
-- ✅ numero_processo_externo: informado pelo usuário
-- ✅ numero_processo_oficial: reservado para futuro
