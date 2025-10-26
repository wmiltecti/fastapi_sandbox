-- Table: public.x_usr

-- DROP TABLE IF EXISTS public.x_usr;

CREATE TABLE IF NOT EXISTS public.x_usr
(
    pk_x_usr integer,
    name character varying(150) COLLATE pg_catalog."default",
    login character varying(25) COLLATE pg_catalog."default",
    password character varying(100) COLLATE pg_catalog."default",
    active integer,
    fk_x_grp integer,
    description character varying(4000) COLLATE pg_catalog."default",
    administrator integer,
    email character varying(50) COLLATE pg_catalog."default",
    fk_x_mod integer,
    changepassword integer,
    bloqueado integer,
    administradoraplicativofiscalizacao integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.x_usr
    OWNER to postgres;

GRANT ALL ON TABLE public.x_usr TO anon;

GRANT ALL ON TABLE public.x_usr TO authenticated;

GRANT ALL ON TABLE public.x_usr TO postgres;

GRANT ALL ON TABLE public.x_usr TO service_role;