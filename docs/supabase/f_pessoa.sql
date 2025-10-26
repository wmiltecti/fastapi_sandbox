-- Table: public.f_pessoa

-- DROP TABLE IF EXISTS public.f_pessoa;

CREATE TABLE IF NOT EXISTS public.f_pessoa
(
    pkpessoa integer,
    fkuser integer,
    tipo integer,
    status integer,
    cpf character varying(14) COLLATE pg_catalog."default",
    nome character varying(150) COLLATE pg_catalog."default",
    datanascimento timestamp without time zone,
    naturalidade character varying(30) COLLATE pg_catalog."default",
    nacionalidade character varying(30) COLLATE pg_catalog."default",
    estadocivil integer,
    sexo integer,
    rg character varying(14) COLLATE pg_catalog."default",
    orgaoemissor character varying(50) COLLATE pg_catalog."default",
    fkestadoemissor integer,
    fkprofissao integer,
    passaporte character varying(18) COLLATE pg_catalog."default",
    datapassaporte timestamp without time zone,
    cnpj character varying(18) COLLATE pg_catalog."default",
    razaosocial character varying(150) COLLATE pg_catalog."default",
    nomefantasia character varying(150) COLLATE pg_catalog."default",
    inscricaoestadual character varying(18) COLLATE pg_catalog."default",
    fkufinscricaoestadual integer,
    datainicioatividade timestamp without time zone,
    inscricaomunicipal character varying(18) COLLATE pg_catalog."default",
    cnaefiscal character varying(14) COLLATE pg_catalog."default",
    simplesnacional integer,
    crccontador character varying(20) COLLATE pg_catalog."default",
    fknaturezajuridica integer,
    fkporte integer,
    identificacaoestrangeira character varying(20) COLLATE pg_catalog."default",
    tipoidentificacaoestrangeira character varying(30) COLLATE pg_catalog."default",
    telefone character varying(20) COLLATE pg_catalog."default",
    telefonealternativo1 character varying(20) COLLATE pg_catalog."default",
    telefonealternativo2 character varying(20) COLLATE pg_catalog."default",
    email character varying(80) COLLATE pg_catalog."default",
    emailalternativo character varying(80) COLLATE pg_catalog."default",
    fax character varying(20) COLLATE pg_catalog."default",
    faxalternativo character varying(20) COLLATE pg_catalog."default",
    complemento character varying(80) COLLATE pg_catalog."default",
    cep character varying(14) COLLATE pg_catalog."default",
    cidade character varying(50) COLLATE pg_catalog."default",
    provincia character varying(50) COLLATE pg_catalog."default",
    fkmunicipio integer,
    fkestado integer,
    fkpais integer,
    statusregimeespecial integer,
    dataregimeespecial timestamp without time zone,
    periodoregimeespecial integer,
    periodopagamentoregimeespecial integer,
    fkcentroinformacao integer,
    datacadastro timestamp without time zone,
    dtype integer,
    numeroconselhoprofissional character varying(20) COLLATE pg_catalog."default",
    fkconselhoprofissional integer,
    fkestadoemissorconselhoprofissional integer,
    caixapostal character varying(10) COLLATE pg_catalog."default",
    endereco character varying(800) COLLATE pg_catalog."default",
    profissao character varying(100) COLLATE pg_catalog."default",
    situacaopessoajuridica integer,
    porteempresa integer,
    filiacaomae character varying(150) COLLATE pg_catalog."default",
    filiacaopai character varying(150) COLLATE pg_catalog."default",
    conjuge_id integer,
    matricula character varying(12) COLLATE pg_catalog."default",
    nomepessoa character varying(150) COLLATE pg_catalog."default",
    numeroidentificacao character varying(20) COLLATE pg_catalog."default",
    nomerazao character varying(150) COLLATE pg_catalog."default",
    permitirvercarscadastrante integer,
    cargo character varying(255) COLLATE pg_catalog."default",
    dataultimaalteracao timestamp without time zone,
    permitirvercarrt integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.f_pessoa
    OWNER to postgres;

GRANT ALL ON TABLE public.f_pessoa TO anon;

GRANT ALL ON TABLE public.f_pessoa TO authenticated;

GRANT ALL ON TABLE public.f_pessoa TO postgres;

GRANT ALL ON TABLE public.f_pessoa TO service_role;