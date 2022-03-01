import pandas as pd
from analyzer.constants import dict_field, NUMBER_MORPH_PARAMETRS

def create_command(level, main_morph_params, dep_morph_params, main_word_param, dep_word_param):
    where_str, params = create_where(main_morph_params, dep_morph_params, main_word_param, dep_word_param)
    if level == 1:
        command = create_command_1(where_str)
    elif level == 2:
        command = create_command_2(where_str)
    elif level == 3:
        command = create_command_3(where_str)
    else:
        print("Ошибка при создании запроса к базе: некорректный уровень МУ (равен", level, ")")
        exit(1)
    return (command, params)

def create_command_1(where_str):
    return "select null, null, " + \
               "create_mark_1(gp.mark, gp.main_morph, gp.dep_morph) as mark, " + \
               "main.s_cl, main.animate, main.gender, main.number, main.case_morph, " + \
               "main.reflection, main.perfective, main.transitive, main.person, main.tense, " + \
               "main.voice, main.degree, main.static, main.prep_type, " + \
               "dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, " + \
               "dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, " + \
               "dep.voice, dep.degree, dep.static, dep.prep_type " + \
               "from gpattern_1_level as gp " + \
               "left join morph_constraints as main " + \
               "on main.id = main_morph " + \
               "left join morph_constraints as dep " + \
               "on dep.id = dep_morph " + \
               where_str + " order by mark desc"

def create_command_2(where_str):
    return "select main_word.name, null, " + \
           "create_mark_2(gp.mark, gp.main_morph, gp.dep_morph, gp.main_word) as mark, " + \
           "main.s_cl, main.animate, main.gender, main.number, main.case_morph, " + \
           "main.reflection, main.perfective, main.transitive, main.person, " + \
           "main.tense, main.voice, main.degree, main.static, main.prep_type, " + \
           "dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, " + \
           "dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, " + \
           "dep.voice, dep.degree, dep.static, dep.prep_type " + \
           "from gpattern_2_level as gp " + \
           "left join morph_constraints as main " + \
           "on main.id = main_morph " + \
           "left join morph_constraints as dep " + \
           "on dep.id = dep_morph " + \
           "left join word as main_word " + \
           "on main_word.id = main_word " + \
           where_str + " order by mark desc"

def create_command_3(where_str):
    return "select main_word.name, dep_word.name, " + \
           "create_mark_3(gp.mark, gp.main_morph, gp.dep_morph, gp.main_word, gp.dep_word) as mark, " + \
           "main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, " + \
           "main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, " + \
           "dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, " + \
           "dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
           "from gpattern_3_level as gp " + \
           "left join morph_constraints as main " + \
           "on main.id = main_morph " + \
           "left join morph_constraints as dep " + \
           "on dep.id = dep_morph " + \
           "left join word as main_word " + \
           "on main_word.id = main_word " + \
           "left join word as dep_word " + \
           "on dep_word.id = dep_word " + \
           where_str + " order by mark desc"

def create_where(main_morph_params, dep_morph_params, main_word_param, dep_word_param):
    if main_word_param:
        where_main_word = "main_word.name = %s"
        if dep_word_param:
            where_dep_word = "dep_word.name = %s "
            res = where_main_word + " and " + where_dep_word
            params = (main_word_param, dep_word_param)
        else:
            res = where_main_word
            params = (main_word_param,)
    else:
        if dep_word_param:
            where_dep_word = "dep_word.name = %s "
            res = where_dep_word
            params = (dep_word_param,)
        else:
            res = ""
            params = ()

    if dep_morph_params:
        where_dep_morph = create_where_dep_morph(dep_morph_params)
        if res != "":
            res = where_dep_morph + " and " + res
        else:
            res = where_dep_morph

    if main_morph_params:
        where_main_morph = create_where_main_morph(main_morph_params)
        if res != "":
            res = where_main_morph + " and " + res
        else:
            res = where_main_morph

    if res != "":
        res = "where " + res
    return res, params

def create_where_dep_morph(dep_morph_params):
    where_dep_morph = ""
    for i in range(len(dep_morph_params)):
        cur_param = dep_morph_params[i]
        s1 = "(dep." + dict_field[cur_param] + " = " + "'" + cur_param + "')"
        where_dep_morph += s1
        if i != len(dep_morph_params) - 1:
            where_dep_morph += " and "
    return where_dep_morph

def create_where_main_morph(main_morph_params):
    where_main_morph = ""
    for i in range(len(main_morph_params)):
        cur_param = main_morph_params[i]
        s1 = "(main." + dict_field[cur_param] + " = " + "'" + cur_param + "')"
        where_main_morph += s1
        if i != len(main_morph_params) - 1:
            where_main_morph += " and "
    return where_main_morph

def get_patterns_pandas(cursor, level, main_morph_params=None, dep_morph_params=None, main_word_param=None,
                        dep_word_param=None):
    command, params = create_command(level, main_morph_params, dep_morph_params, main_word_param, dep_word_param)
    cursor.execute(command, params)
    res = cursor.fetchall()
    names = ['s_cl', 'animate', 'gender', 'number', 'case_morph', 'reflection', 'perfective', 'transitive', 'person',
             'tense', 'voice', 'degree', 'static', 'prep_type']
    main_names = list(map(lambda x: 'main_' + x, names))
    dep_names = list(map(lambda x: 'dep_' + x, names))
    df = pd.DataFrame(res, columns=['main_word', 'dep_word', 'mark'] + main_names + dep_names)
    for column in df.columns:
        if (df[column] == 'not_imp').all():
            df.drop(column, axis='columns', inplace=True)
    df['mark'] = [round(n, 2) for n in df['mark']]
    return df