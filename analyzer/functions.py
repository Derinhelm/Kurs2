from analyzer.constants import dict_field, NUMBER_MORPH_PARAMETRS
from analyzer.patterns import GPattern


def create_command(level, main_morph_params, main_word_param):
    if level == 1:
        command = create_command_1(main_morph_params)
        params = ()
    elif level == 2:
        command = create_command_2(main_morph_params)
        params = (main_word_param,)
    elif level == 3:
        command = create_command_3(main_morph_params)
        params = (main_word_param,)
    else:
        print("Ошибка при создании запроса к базе: некорректный уровень МУ (равен", level, ")")
        exit(1)
    return command, params


def create_command_1(main_morph_params):
    where_str = create_where_main_morph(main_morph_params)
    begin = "with " + \
            "main_morph_t as " + \
            "(select id, s_cl, animate, gender, number, case_morph, reflection, perfective, transitive, person, tense, voice, degree, static, prep_type from morph_constraints where "

    end = "), " + \
          "gp as " + \
          "(select main_morph, dep_morph, mark from gpattern_1_level where main_morph in (select id from main_morph_t)) " + \
          "select null, null, create_mark_1(gp.mark, gp.main_morph, gp.dep_morph) as mark, main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
          "from gp join main_morph_t as main on gp.main_morph=main.id join morph_constraints as dep on gp.dep_morph=dep.id order by mark desc;"

    return begin + where_str + end


def create_command_2(main_morph_params):
    where_str = create_where_main_morph(main_morph_params)

    begin = "with main_morph_t as (select id, s_cl, animate, gender, number, case_morph, reflection, perfective, transitive, person, tense, voice, degree, static, prep_type from morph_constraints where "

    end = "), " + \
          "main_word_t as (select id, name from word where name=%s), " + \
          "gp as (select main_morph, dep_morph, main_word, mark from gpattern_2_level where main_morph in (select id from main_morph_t) and main_word = (select id from main_word_t)) " + \
          "select main_w.name, null, create_mark_2(gp.mark, gp.main_morph, gp.dep_morph, gp.main_word) as mark, main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
          "from gp " + \
          "join main_morph_t as main on gp.main_morph=main.id " + \
          "join morph_constraints as dep on gp.dep_morph=dep.id " + \
          "join main_word_t as main_w on gp.main_word=main_w.id " + \
          "order by mark desc;"

    return begin + where_str + end


def create_command_3(main_morph_params):
    where_str = create_where_main_morph(main_morph_params)

    begin = "with main_morph_t as (select id, s_cl, animate, gender, number, case_morph, reflection, perfective, transitive, person, tense, voice, degree, static, prep_type from morph_constraints where "

    end = "), " + \
          "main_word_t as (select id, name from word where name=%s)," + \
          "gp as (select main_morph, dep_morph, main_word, dep_word, mark from gpattern_3_level where main_morph in (select id from main_morph_t) and main_word = (select id from main_word_t)) " + \
          "select main_w.name, dep_w.name, create_mark_3(gp.mark, gp.main_morph, gp.dep_morph, gp.main_word, gp.dep_word) as mark, main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
          "from gp " + \
          "join main_morph_t as main on gp.main_morph=main.id " + \
          "join morph_constraints as dep on gp.dep_morph=dep.id " + \
          "join main_word_t as main_w on gp.main_word=main_w.id " + \
          "join word as dep_w on gp.dep_word=dep_w.id " + \
          "order by mark desc;"

    return begin + where_str + end


def create_where_main_morph(main_morph_params):
    where_main_morph = ""
    for i in range(len(main_morph_params)):
        cur_param = main_morph_params[i]
        s1 = "(" + dict_field[cur_param] + " = " + "'" + cur_param + "'"
        s1 += " or " + dict_field[cur_param] + " = " + "'not_imp')"
        where_main_morph += s1
        if i != len(main_morph_params) - 1:
            where_main_morph += " and "
    return where_main_morph


def get_patterns_from_db(cursor, level, lexemes=None, main_morph_params=None, main_word_param=None):
    command, params = create_command(level, main_morph_params, main_word_param)
    # print(command)
    # print(params)
    cursor.execute(command, params)
    res = cursor.fetchall()
    patterns_list = []
    for pattern in res:
        dw = pattern[1]
        if level != 3 or (level == 3 and dw in lexemes):
    #учитываем МУ, если в МУ 3 уровня ограничению на лексему зависимого слова удовлетворяет хотя бы один вариант разбора словоформы в предложении
            mw = pattern[0]
            mark = pattern[2]
            main_constr = []
            dep_constr = []
            for i in range(3, NUMBER_MORPH_PARAMETRS + 3):
                if pattern[i] != 'not_imp':
                    main_constr.append(pattern[i])
            for i in range(3 + NUMBER_MORPH_PARAMETRS, 3 + 2 * NUMBER_MORPH_PARAMETRS):
                if pattern[i] != 'not_imp':
                    dep_constr.append(pattern[i])
            new_pattern = GPattern(level, mw, dw, mark,
                                   main_constr, dep_constr)
            # toDO
            if 'preposition' in new_pattern.main_word_constraints and 'adverb' in new_pattern.dependent_word_constraints:
                print("prep + adverb")
            else:
                patterns_list.append(new_pattern)
    return patterns_list
