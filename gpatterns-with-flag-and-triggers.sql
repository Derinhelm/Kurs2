-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.1-beta
-- PostgreSQL version: 10.0
-- Project Site: pgmodeler.com.br
-- Model Author: ---

SET check_function_bodies = false;
-- ddl-end --


-- Database creation must be done outside an multicommand file.
-- These commands were put in this file only for convenience.
-- -- object: gpatterns | type: DATABASE --
-- -- DROP DATABASE IF EXISTS gpatterns;
-- CREATE DATABASE gpatterns
-- ;
-- -- ddl-end --
-- 

-- object: public.gpattern_3_level | type: TABLE --
-- DROP TABLE IF EXISTS public.gpattern_3_level CASCADE;
CREATE TABLE public.gpattern_3_level(
	id serial NOT NULL,
	main_morph integer,
	dep_morph integer,
	main_word integer,
	dep_word integer,
	mark double precision,
	CONSTRAINT prim_k_3 PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE public.gpattern_3_level OWNER TO postgres;
-- ddl-end --

-- object: public.gpattern_2_level | type: TABLE --
-- DROP TABLE IF EXISTS public.gpattern_2_level CASCADE;
CREATE TABLE public.gpattern_2_level(
	id serial NOT NULL,
	main_morph integer,
	dep_morph integer,
	main_word integer,
	mark double precision,
	CONSTRAINT prim_k_2 PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE public.gpattern_2_level OWNER TO postgres;
-- ddl-end --

-- object: public.gpattern_1_level | type: TABLE --
-- DROP TABLE IF EXISTS public.gpattern_1_level CASCADE;
CREATE TABLE public.gpattern_1_level(
	id serial NOT NULL,
	main_morph integer,
	dep_morph integer,
	mark double precision,
	CONSTRAINT prim_k_1 PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE public.gpattern_1_level OWNER TO postgres;
-- ddl-end --

-- object: public.es_cl | type: TYPE --
-- DROP TYPE IF EXISTS public.es_cl CASCADE;
CREATE TYPE public.es_cl AS
 ENUM ('noun','personalpronoun','reflexivepronoun','pronoun','name','adjective','possesiveadjective','pronounadjective','numberordinal','participle','shortadjective','shortparticiple','comparative','verb','unpersonalverb','frequentativeverb','gerund','numberone','numbertwo','numberthree','number','numberbiform','adverb','preposition','conjunction','predicative','particle','interjection','acronym','s_cl_any','not_imp');
-- ddl-end --
ALTER TYPE public.es_cl OWNER TO postgres;
-- ddl-end --

-- object: public.eanimate | type: TYPE --
-- DROP TYPE IF EXISTS public.eanimate CASCADE;
CREATE TYPE public.eanimate AS
 ENUM ('animate','unanimate','animate_any','not_imp');
-- ddl-end --
ALTER TYPE public.eanimate OWNER TO postgres;
-- ddl-end --

-- object: public.egender | type: TYPE --
-- DROP TYPE IF EXISTS public.egender CASCADE;
CREATE TYPE public.egender AS
 ENUM ('male','female','neuter','malefemale','maleorfemale','gender_any','not_imp');
-- ddl-end --
ALTER TYPE public.egender OWNER TO postgres;
-- ddl-end --

-- object: public.enumber | type: TYPE --
-- DROP TYPE IF EXISTS public.enumber CASCADE;
CREATE TYPE public.enumber AS
 ENUM ('single','plural','number_any','not_imp');
-- ddl-end --
ALTER TYPE public.enumber OWNER TO postgres;
-- ddl-end --

-- object: public.ecase | type: TYPE --
-- DROP TYPE IF EXISTS public.ecase CASCADE;
CREATE TYPE public.ecase AS
 ENUM ('nominative','genitive','dative','accusative','instrumental','prepositional','case_any','not_imp');
-- ddl-end --
ALTER TYPE public.ecase OWNER TO postgres;
-- ddl-end --

-- object: public.ereflection | type: TYPE --
-- DROP TYPE IF EXISTS public.ereflection CASCADE;
CREATE TYPE public.ereflection AS
 ENUM ('reflexive','unreflexive','reflexive_form','reflection_any','not_imp');
-- ddl-end --
ALTER TYPE public.ereflection OWNER TO postgres;
-- ddl-end --

-- object: public.eperfective | type: TYPE --
-- DROP TYPE IF EXISTS public.eperfective CASCADE;
CREATE TYPE public.eperfective AS
 ENUM ('perfective','unperfective','perfective_any','not_imp');
-- ddl-end --
ALTER TYPE public.eperfective OWNER TO postgres;
-- ddl-end --

-- object: public.etransitive | type: TYPE --
-- DROP TYPE IF EXISTS public.etransitive CASCADE;
CREATE TYPE public.etransitive AS
 ENUM ('transitive','untransitive','transitive_any','not_imp');
-- ddl-end --
ALTER TYPE public.etransitive OWNER TO postgres;
-- ddl-end --

-- object: public.eperson | type: TYPE --
-- DROP TYPE IF EXISTS public.eperson CASCADE;
CREATE TYPE public.eperson AS
 ENUM ('first','second','third','person_any','not_imp');
-- ddl-end --
ALTER TYPE public.eperson OWNER TO postgres;
-- ddl-end --

-- object: public.etense | type: TYPE --
-- DROP TYPE IF EXISTS public.etense CASCADE;
CREATE TYPE public.etense AS
 ENUM ('infinitive','present','past','future','imperative','tense_any','not_imp');
-- ddl-end --
ALTER TYPE public.etense OWNER TO postgres;
-- ddl-end --

-- object: public.evoice | type: TYPE --
-- DROP TYPE IF EXISTS public.evoice CASCADE;
CREATE TYPE public.evoice AS
 ENUM ('active','passive','voice_any','not_imp');
-- ddl-end --
ALTER TYPE public.evoice OWNER TO postgres;
-- ddl-end --

-- object: public.edegree | type: TYPE --
-- DROP TYPE IF EXISTS public.edegree CASCADE;
CREATE TYPE public.edegree AS
 ENUM ('strong','weak','degree_any','not_imp');
-- ddl-end --
ALTER TYPE public.edegree OWNER TO postgres;
-- ddl-end --

-- object: public.estatic | type: TYPE --
-- DROP TYPE IF EXISTS public.estatic CASCADE;
CREATE TYPE public.estatic AS
 ENUM ('true','false','not_imp');
-- ddl-end --
ALTER TYPE public.estatic OWNER TO postgres;
-- ddl-end --

-- object: public.epreptype | type: TYPE --
-- DROP TYPE IF EXISTS public.epreptype CASCADE;
CREATE TYPE public.epreptype AS
 ENUM ('a','dap','gai','ai','ap','d','gd','g','gi','i','p','not_imp');
-- ddl-end --
ALTER TYPE public.epreptype OWNER TO postgres;
-- ddl-end --

-- object: public.word | type: TABLE --
-- DROP TABLE IF EXISTS public.word CASCADE;
CREATE TABLE public.word(
	id serial NOT NULL,
	name varchar(100),
	CONSTRAINT prim_k_w PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE public.word OWNER TO postgres;
-- ddl-end --

-- object: public.morph_constraints | type: TABLE --
-- DROP TABLE IF EXISTS public.morph_constraints CASCADE;
CREATE TABLE public.morph_constraints(
	id serial NOT NULL,
	s_cl public.es_cl,
	animate public.eanimate,
	gender public.egender,
	number public.enumber,
	case_morph public.ecase,
	reflection public.ereflection,
	perfective public.eperfective,
	transitive public.etransitive,
	person public.eperson,
	tense public.etense,
	voice public.evoice,
	degree public.edegree,
	static public.estatic,
	prep_type public.epreptype,
	CONSTRAINT prim_k_m PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE public.morph_constraints OWNER TO postgres;
-- ddl-end --

-- object: public.create_mark_1 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.create_mark_1(double precision,integer,integer) CASCADE;
CREATE FUNCTION public.create_mark_1 ( all_mark double precision,  mm integer,  dm integer)
	RETURNS double precision
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
select all_mark / get_mark_1_dep_morph(mm) / get_mark_1_dep_morph(dm)
$$;
-- ddl-end --
ALTER FUNCTION public.create_mark_1(double precision,integer,integer) OWNER TO postgres;
-- ddl-end --

-- object: public.create_mark_2 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.create_mark_2(double precision,integer,integer,integer) CASCADE;
CREATE FUNCTION public.create_mark_2 ( all_mark double precision,  mm integer,  dm integer,  mw integer)
	RETURNS double precision
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
select all_mark / get_mark_2_main_morph(mm) /get_mark_2_dep_morph(dm)/get_mark_2_main_word(mw)
$$;
-- ddl-end --
ALTER FUNCTION public.create_mark_2(double precision,integer,integer,integer) OWNER TO postgres;
-- ddl-end --

-- object: public.create_mark_3 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.create_mark_3(double precision,integer,integer,integer,integer) CASCADE;
CREATE FUNCTION public.create_mark_3 ( all_mark double precision,  mm integer,  dm integer,  mw integer,  dw integer)
	RETURNS double precision
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
select all_mark /get_mark_3_main_morph(mm) / get_mark_3_dep_morph(dm) / get_mark_3_main_word(mw)/ get_mark_3_dep_word(dw)
$$;
-- ddl-end --
ALTER FUNCTION public.create_mark_3(double precision,integer,integer,integer,integer) OWNER TO postgres;
-- ddl-end --

-- object: public.morph_occurence | type: TABLE --
-- DROP TABLE IF EXISTS public.morph_occurence CASCADE;
CREATE TABLE public.morph_occurence(
	id integer NOT NULL,
	main_1 double precision DEFAULT 0,
	dep_1 double precision DEFAULT 0,
	main_2 double precision DEFAULT 0,
	dep_2 double precision DEFAULT 0,
	main_3 double precision DEFAULT 0,
	dep_3 double precision DEFAULT 0,
	CONSTRAINT morph_occurence_pk PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE public.morph_occurence OWNER TO postgres;
-- ddl-end --

-- object: public.word_occurence | type: TABLE --
-- DROP TABLE IF EXISTS public.word_occurence CASCADE;
CREATE TABLE public.word_occurence(
	id integer NOT NULL,
	main_2 double precision DEFAULT 0,
	main_3 double precision DEFAULT 0,
	dep_3 double precision DEFAULT 0,
	CONSTRAINT word_occurence_pk PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE public.word_occurence OWNER TO postgres;
-- ddl-end --

-- object: public.change_main_morph_1 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_main_morph_1(integer,double precision) CASCADE;
CREATE FUNCTION public.change_main_morph_1 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.morph_occurence (id, main_1)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET main_1 = public.morph_occurence.main_1  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_main_morph_1(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_main_morph_1(integer,double precision) IS 'добавляем к оценке из таблицы morph_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_dep_morph_1 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_dep_morph_1(integer,double precision) CASCADE;
CREATE FUNCTION public.change_dep_morph_1 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.morph_occurence (id, dep_1)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET dep_1 = public.morph_occurence.dep_1  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_dep_morph_1(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_dep_morph_1(integer,double precision) IS 'добавляем к оценке из таблицы morph_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_main_morph_2 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_main_morph_2(integer,double precision) CASCADE;
CREATE FUNCTION public.change_main_morph_2 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.morph_occurence (id, main_2)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET main_2 = public.morph_occurence.main_2  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_main_morph_2(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_main_morph_2(integer,double precision) IS 'добавляем к оценке из таблицы morph_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_dep_morph_2 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_dep_morph_2(integer,double precision) CASCADE;
CREATE FUNCTION public.change_dep_morph_2 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.morph_occurence (id, dep_2)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET dep_2 = public.morph_occurence.dep_2  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_dep_morph_2(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_dep_morph_2(integer,double precision) IS 'добавляем к оценке из таблицы morph_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_main_morph_3 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_main_morph_3(integer,double precision) CASCADE;
CREATE FUNCTION public.change_main_morph_3 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.morph_occurence (id, main_3)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET main_3 = public.morph_occurence.main_3  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_main_morph_3(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_main_morph_3(integer,double precision) IS 'добавляем к оценке из таблицы morph_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_dep_morph_3 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_dep_morph_3(integer,double precision) CASCADE;
CREATE FUNCTION public.change_dep_morph_3 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.morph_occurence (id, dep_3)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET dep_3 = public.morph_occurence.dep_3  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_dep_morph_3(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_dep_morph_3(integer,double precision) IS 'добавляем к оценке из таблицы morph_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_dep_word_3 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_dep_word_3(integer,double precision) CASCADE;
CREATE FUNCTION public.change_dep_word_3 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.word_occurence (id, dep_3)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET dep_3 = public.word_occurence.dep_3  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_dep_word_3(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_dep_word_3(integer,double precision) IS 'добавляем к оценке из таблицы word_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_main_word_2 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_main_word_2(integer,double precision) CASCADE;
CREATE FUNCTION public.change_main_word_2 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.word_occurence (id, main_2)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET main_2 = public.word_occurence.main_2  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_main_word_2(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_main_word_2(integer,double precision) IS 'добавляем к оценке из таблицы word_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_1 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_1() CASCADE;
CREATE FUNCTION public.change_1 ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    mark public.gpattern_1_level.mark%TYPE ;
    mm  public.gpattern_1_level.main_morph%TYPE ;
    dm  public.gpattern_1_level.dep_morph%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
				    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
				        mark := new.mark;
				        mm := new.main_morph;
				        dm := new.dep_morph;
				    ELSIF TG_OP = 'DELETE' THEN
				        mark := -old.mark;
				        mm := old.main_morph;
				        dm := old.dep_morph;
				    END IF;
				    perform public.change_main_morph_1(mm, mark), public.change_dep_morph_1(dm, mark);
    END IF;
    return null;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.change_1() OWNER TO postgres;
-- ddl-end --

-- object: public.change_main_word_3 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_main_word_3(integer,double precision) CASCADE;
CREATE FUNCTION public.change_main_word_3 ( id_param integer,  new_mark double precision)
	RETURNS void
	LANGUAGE sql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
INSERT INTO public.word_occurence (id, main_3)
VALUES (id_param, new_mark)
ON CONFLICT (id) DO UPDATE SET main_3 = public.word_occurence.main_3  + new_mark;
$$;
-- ddl-end --
ALTER FUNCTION public.change_main_word_3(integer,double precision) OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.change_main_word_3(integer,double precision) IS 'добавляем к оценке из таблицы word_occurence оценку-параметр';
-- ddl-end --

-- object: public.change_2 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_2() CASCADE;
CREATE FUNCTION public.change_2 ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    mark public.gpattern_2_level.mark%TYPE ;
    mm  public.gpattern_2_level.main_morph%TYPE ;
    dm  public.gpattern_2_level.dep_morph%TYPE ;
    mw  public.gpattern_2_level.main_word%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
				    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
				        mark := new.mark;
				        mm := new.main_morph;
				        dm := new.dep_morph;
				        mw := new.main_word;
				    ELSIF TG_OP = 'DELETE' THEN
				        mark := -old.mark;
				        mm := old.main_morph;
				        dm := old.dep_morph;
				        mw := old.main_word;
				    END IF;
				    perform public.change_main_morph_2(mm, mark), public.change_dep_morph_2(dm, mark), public.change_main_word_2(mw, mark);
    END IF;
    return null;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.change_2() OWNER TO postgres;
-- ddl-end --

-- object: public.change_3 | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.change_3() CASCADE;
CREATE FUNCTION public.change_3 ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    mark public.gpattern_3_level.mark%TYPE ;
    mm  public.gpattern_3_level.main_morph%TYPE ;
    dm  public.gpattern_3_level.dep_morph%TYPE ;
    mw  public.gpattern_3_level.main_word%TYPE ;
    dw  public.gpattern_3_level.dep_word%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
				    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
				        mark := new.mark;
				        mm := new.main_morph;
				        dm := new.dep_morph;
				        mw := new.main_word;
				        dw := new.dep_word;
				    ELSIF TG_OP = 'DELETE' THEN
				        mark := -old.mark;
				        mm := old.main_morph;
				        dm := old.dep_morph;
				        mw := old.main_word;
				        dw := old.dep_word;
				    END IF;
				    perform public.change_main_morph_3(mm, mark), public.change_dep_morph_3(dm, mark), public.change_main_word_3(mw, mark), public.change_dep_word_3(dw, mark);
    END IF;
    return null;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.change_3() OWNER TO postgres;
-- ddl-end --

-- object: trigger_1 | type: TRIGGER --
-- DROP TRIGGER IF EXISTS trigger_1 ON public.gpattern_1_level CASCADE;
CREATE TRIGGER trigger_1
	AFTER INSERT OR DELETE OR UPDATE
	ON public.gpattern_1_level
	FOR EACH ROW
	EXECUTE PROCEDURE public.change_1();
-- ddl-end --

-- object: trigger_2 | type: TRIGGER --
-- DROP TRIGGER IF EXISTS trigger_2 ON public.gpattern_2_level CASCADE;
CREATE TRIGGER trigger_2
	AFTER INSERT OR DELETE OR UPDATE
	ON public.gpattern_2_level
	FOR EACH ROW
	EXECUTE PROCEDURE public.change_2();
-- ddl-end --

-- object: trigger_3 | type: TRIGGER --
-- DROP TRIGGER IF EXISTS trigger_3 ON public.gpattern_3_level CASCADE;
CREATE TRIGGER trigger_3
	AFTER INSERT OR DELETE OR UPDATE
	ON public.gpattern_3_level
	FOR EACH ROW
	EXECUTE PROCEDURE public.change_3();
-- ddl-end --

-- object: public.flag_table | type: TABLE --
-- DROP TABLE IF EXISTS public.flag_table CASCADE;
CREATE TABLE public.flag_table(
	occurence_relevant bool DEFAULT false
);
-- ddl-end --
COMMENT ON TABLE public.flag_table IS 'occurence_relevant=true - берем данные из таблиц occurence, иначе считаем заново';
-- ddl-end --
ALTER TABLE public.flag_table OWNER TO postgres;
-- ddl-end --

INSERT INTO public.flag_table (occurence_relevant) VALUES (E'false');
-- ddl-end --

-- object: public.get_mark_1_main_morph | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_1_main_morph(integer) CASCADE;
CREATE FUNCTION public.get_mark_1_main_morph ( mm integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_1_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select main_1 from morph_occurence where id = mm into res;
    ELSE
        select sum(mark) from gpattern_1_level where main_morph = mm into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_1_main_morph(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_1_dep_morph | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_1_dep_morph(integer) CASCADE;
CREATE FUNCTION public.get_mark_1_dep_morph ( dm integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_1_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select dep_1 from morph_occurence where id = dm into res;
    ELSE
        select sum(mark) from gpattern_1_level where dep_morph = dm into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_1_dep_morph(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_2_dep_morph | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_2_dep_morph(integer) CASCADE;
CREATE FUNCTION public.get_mark_2_dep_morph ( dm integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_2_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select dep_2  from morph_occurence where id = dm into res;
    ELSE
        select sum(mark) from gpattern_2_level where dep_morph = dm into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_2_dep_morph(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_2_main_morph | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_2_main_morph(integer) CASCADE;
CREATE FUNCTION public.get_mark_2_main_morph ( mm integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_2_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select main_2 from morph_occurence where id = mm into res;
    ELSE
         select sum(mark) from gpattern_2_level where main_morph = mm into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_2_main_morph(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_2_main_word | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_2_main_word(integer) CASCADE;
CREATE FUNCTION public.get_mark_2_main_word ( mw integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_2_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select main_2 from word_occurence where id = mw into res;
    ELSE
        select sum(mark) from gpattern_2_level where main_word = mw into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_2_main_word(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_3_dep_morph | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_3_dep_morph(integer) CASCADE;
CREATE FUNCTION public.get_mark_3_dep_morph ( dm integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_3_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select dep_3 from morph_occurence where id = dm into res;
    ELSE
         select sum(mark) from gpattern_3_level where dep_morph = dm into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_3_dep_morph(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_3_main_morph | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_3_main_morph(integer) CASCADE;
CREATE FUNCTION public.get_mark_3_main_morph ( mm integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_3_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select main_3 from morph_occurence where id = mm into res;
    ELSE
        select sum(mark) from gpattern_3_level where main_morph = mm into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_3_main_morph(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_3_main_word | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_3_main_word(integer) CASCADE;
CREATE FUNCTION public.get_mark_3_main_word ( mw integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_3_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select main_3 from word_occurence where id = mw into res;
    ELSE
         select sum(mark) from gpattern_3_level where main_word = mw into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_3_main_word(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.get_mark_3_dep_word | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.get_mark_3_dep_word(integer) CASCADE;
CREATE FUNCTION public.get_mark_3_dep_word ( dw integer)
	RETURNS double precision
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
DECLARE
    res public.gpattern_3_level.mark%TYPE ;
BEGIN
    IF (select occurence_relevant  from public.flag_table) THEN
        select dep_3 from word_occurence where id = dw into res;
    ELSE
         select sum(mark) from gpattern_3_level where dep_word = dw into res;
    END IF;
    return res;
END ;
$$;
-- ddl-end --
ALTER FUNCTION public.get_mark_3_dep_word(integer) OWNER TO postgres;
-- ddl-end --

-- object: public.null_fun | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.null_fun() CASCADE;
CREATE FUNCTION public.null_fun ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
begin
				return null;
end;
$$;
-- ddl-end --
ALTER FUNCTION public.null_fun() OWNER TO postgres;
-- ddl-end --

-- object: ban_trigger | type: TRIGGER --
-- DROP TRIGGER IF EXISTS ban_trigger ON public.flag_table CASCADE;
CREATE TRIGGER ban_trigger
	BEFORE INSERT OR DELETE 
	ON public.flag_table
	FOR EACH ROW
	EXECUTE PROCEDURE public.null_fun();
-- ddl-end --

-- object: public.upd_occurence_relevant | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.upd_occurence_relevant() CASCADE;
CREATE FUNCTION public.upd_occurence_relevant ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
begin
				if not old.occurence_relevant and new.occurence_relevant then
													with 
													t1 as (select sum(mark) as mm1, main_morph as id from gpattern_1_level group by main_morph), 
													t2 as (select sum(mark) as dm1, dep_morph as id from gpattern_1_level group by dep_morph),
													t3 as (select sum(mark) as mm2, main_morph as id from gpattern_2_level group by main_morph),
													t4 as (select sum(mark) as dm2, dep_morph as id from gpattern_2_level group by dep_morph),
													t5 as (select sum(mark) as mm3, main_morph as id from gpattern_3_level group by main_morph),
													t6 as (select sum(mark) as dm3, dep_morph as id from gpattern_3_level group by dep_morph),
													t as (select t1.mm1, t2.dm1, t3.mm2, t4.dm2, t5.mm3, t6.dm3, t1.id from t1 full join t2 on t1.id = t2.id full join t3 on t1.id = t3.id full join t4 on t1.id = t4.id full join t5 on t1.id = t5.id full join t6 on t1.id = t6.id)
													update public.morph_occurence set (main_1, dep_1, main_2, dep_2, main_3, dep_3) = (t.mm1, t.dm1, t.mm2, t.dm2, t.mm3, t.dm3)  from t where t.id = morph_occurence.id;
											  with t1 as (select sum(mark) as mw2, main_word as id from gpattern_2_level group by main_word), 
											  t2 as (select sum(mark) as mw3, main_word as id from gpattern_3_level group by main_word),
											  t3 as (select sum(mark) as dw3, dep_word as id from gpattern_3_level group by dep_word),
											  	t as (select t1.mw2, t2.mw3, t3.dw3, t1.id from t1 full join t2 on t1.id = t2.id full join t3 on t1.id = t3.id )
											  update public.word_occurence set (main_2, main_3, dep_3) = (t.mw2, t.mw3, t.dw3)  from t where t.id = word_occurence.id;
				end if;
				return null;
end;
$$;
-- ddl-end --
ALTER FUNCTION public.upd_occurence_relevant() OWNER TO postgres;
-- ddl-end --

-- object: public.word_id_change | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.word_id_change() CASCADE;
CREATE FUNCTION public.word_id_change ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
				    IF TG_OP = 'INSERT'  THEN
				        insert into public.word_occurence(id) values (new.id);
				    ELSIF TG_OP = 'DELETE' THEN
				        delete from public.word_occurence where id = old.id;
				    END IF;
				    RETURN null;
END;
$$;
-- ddl-end --
ALTER FUNCTION public.word_id_change() OWNER TO postgres;
-- ddl-end --

-- object: word_id_trigger | type: TRIGGER --
-- DROP TRIGGER IF EXISTS word_id_trigger ON public.word CASCADE;
CREATE TRIGGER word_id_trigger
	AFTER INSERT OR DELETE 
	ON public.word
	FOR EACH ROW
	EXECUTE PROCEDURE public.word_id_change();
-- ddl-end --

-- object: public.morph_id_change | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.morph_id_change() CASCADE;
CREATE FUNCTION public.morph_id_change ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
				    IF TG_OP = 'INSERT'  THEN
				        insert into public.morph_occurence(id) values (new.id);
				    ELSIF TG_OP = 'DELETE' THEN
				        delete from public.morph_occurence where id = old.id;
				    END IF;
				    RETURN null;
END;
$$;
-- ddl-end --
ALTER FUNCTION public.morph_id_change() OWNER TO postgres;
-- ddl-end --

-- object: morph_id_trigger | type: TRIGGER --
-- DROP TRIGGER IF EXISTS morph_id_trigger ON public.morph_constraints CASCADE;
CREATE TRIGGER morph_id_trigger
	AFTER INSERT OR DELETE 
	ON public.morph_constraints
	FOR EACH ROW
	EXECUTE PROCEDURE public.morph_id_change();
-- ddl-end --

-- object: upd_trigger | type: TRIGGER --
-- DROP TRIGGER IF EXISTS upd_trigger ON public.flag_table CASCADE;
CREATE TRIGGER upd_trigger
	AFTER UPDATE
	ON public.flag_table
	FOR EACH ROW
	EXECUTE PROCEDURE public.upd_occurence_relevant();
-- ddl-end --

-- object: r_d_mo_1 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_3_level DROP CONSTRAINT IF EXISTS r_d_mo_1 CASCADE;
ALTER TABLE public.gpattern_3_level ADD CONSTRAINT r_d_mo_1 FOREIGN KEY (dep_morph)
REFERENCES public.morph_constraints (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_m_mo_1 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_3_level DROP CONSTRAINT IF EXISTS r_m_mo_1 CASCADE;
ALTER TABLE public.gpattern_3_level ADD CONSTRAINT r_m_mo_1 FOREIGN KEY (main_morph)
REFERENCES public.morph_constraints (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_d_w_3 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_3_level DROP CONSTRAINT IF EXISTS r_d_w_3 CASCADE;
ALTER TABLE public.gpattern_3_level ADD CONSTRAINT r_d_w_3 FOREIGN KEY (dep_word)
REFERENCES public.word (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_m_w_3 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_3_level DROP CONSTRAINT IF EXISTS r_m_w_3 CASCADE;
ALTER TABLE public.gpattern_3_level ADD CONSTRAINT r_m_w_3 FOREIGN KEY (main_word)
REFERENCES public.word (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_d_mo_2 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_2_level DROP CONSTRAINT IF EXISTS r_d_mo_2 CASCADE;
ALTER TABLE public.gpattern_2_level ADD CONSTRAINT r_d_mo_2 FOREIGN KEY (dep_morph)
REFERENCES public.morph_constraints (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_m_mo_2 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_2_level DROP CONSTRAINT IF EXISTS r_m_mo_2 CASCADE;
ALTER TABLE public.gpattern_2_level ADD CONSTRAINT r_m_mo_2 FOREIGN KEY (main_morph)
REFERENCES public.morph_constraints (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_m_w_2 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_2_level DROP CONSTRAINT IF EXISTS r_m_w_2 CASCADE;
ALTER TABLE public.gpattern_2_level ADD CONSTRAINT r_m_w_2 FOREIGN KEY (main_word)
REFERENCES public.word (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_m_mo_1 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_1_level DROP CONSTRAINT IF EXISTS r_m_mo_1 CASCADE;
ALTER TABLE public.gpattern_1_level ADD CONSTRAINT r_m_mo_1 FOREIGN KEY (main_morph)
REFERENCES public.morph_constraints (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: r_d_mo_1 | type: CONSTRAINT --
-- ALTER TABLE public.gpattern_1_level DROP CONSTRAINT IF EXISTS r_d_mo_1 CASCADE;
ALTER TABLE public.gpattern_1_level ADD CONSTRAINT r_d_mo_1 FOREIGN KEY (dep_morph)
REFERENCES public.morph_constraints (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: occurense_to_constraints | type: CONSTRAINT --
-- ALTER TABLE public.morph_occurence DROP CONSTRAINT IF EXISTS occurense_to_constraints CASCADE;
ALTER TABLE public.morph_occurence ADD CONSTRAINT occurense_to_constraints FOREIGN KEY (id)
REFERENCES public.morph_constraints (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: occurence_word | type: CONSTRAINT --
-- ALTER TABLE public.word_occurence DROP CONSTRAINT IF EXISTS occurence_word CASCADE;
ALTER TABLE public.word_occurence ADD CONSTRAINT occurence_word FOREIGN KEY (id)
REFERENCES public.word (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --


