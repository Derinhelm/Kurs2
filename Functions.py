from Types import *
import psycopg2
import pandas as pd

def create_comand(level, where_str):
    if level == 1:
        return "select null, null, " + \
               "create_mark_1(gp.mark, gp.main_morph, gp.dep_morph) as mark, " + \
                "main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, " + \
                 "dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
        "from gpattern_1_level as gp " + \
        "left join morph_constraints as main " + \
        "on main.id = main_morph " + \
        "left join morph_constraints as dep " + \
        "on dep.id = dep_morph " + \
        where_str + " order by mark desc"
    if level == 2:
        return "select main_word.name, null, " + \
               "create_mark_2(gp.mark, gp.main_morph, gp.dep_morph, gp.main_word) as mark, " + \
                "main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, " + \
                 "dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
        "from gpattern_2_level as gp " + \
        "left join morph_constraints as main " + \
        "on main.id = main_morph " + \
        "left join morph_constraints as dep " + \
        "on dep.id = dep_morph " + \
        "left join word as main_word " + \
        "on main_word.id = main_word " + \
        where_str + " order by mark desc"
    # level = 3
    return "select main_word.name, dep_word.name, " + \
           "create_mark_3(gp.mark, gp.main_morph, gp.dep_morph, gp.main_word, gp.dep_word) as mark, " + \
    "main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, " + \
                 "dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
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


def create_where(strict, mainMorphParams, depMorphParams, mainWordParam, depWordParam):
    if mainWordParam:
        whereMainWord = "main_word.name = %s"
        if depWordParam:
            whereDepWord = "dep_word.name = %s "
            res = whereMainWord + " and " + whereDepWord
            params = (mainWordParam, depWordParam)
        else:
            res = whereMainWord
            params = (mainWordParam,)
    else:
        if depWordParam:
            whereDepWord = "dep_word.name = %s "
            res = whereDepWord
            params = (depWordParam,)
        else:
            res = ""
            params = ()

    if depMorphParams:
        whereDepMorph = ""
        for i in range(len(depMorphParams)):
            curParam = depMorphParams[i]
            s1 = "(dep." + dictField[curParam] + " = " + "'" + curParam + "'"
            if not strict:
                s1 += " or dep." + dictField[curParam] + " = " + "'not_imp')"
            else:
                s1 += ")"
            whereDepMorph += s1
            if i != len(depMorphParams) - 1:
                whereDepMorph += " and "
        if res != "":
            res = whereDepMorph + " and " + res
        else:
            res = whereDepMorph

    if mainMorphParams:
        whereMainMorph = ""
        for i in range(len(mainMorphParams)):
            curParam = mainMorphParams[i]
            s1 = "(main." + dictField[curParam] + " = " + "'" + curParam + "'"
            if not strict:
                s1 += " or main." + dictField[curParam] + " = " + "'not_imp')"
            else:
                s1 += ")"
            whereMainMorph += s1
            if i != len(mainMorphParams) - 1:
                whereMainMorph += " and "
        if res != "":
            res = whereMainMorph + " and " + res
        else:
            res = whereMainMorph
    if res != "":
        res = "where " + res
    return (res, params)

def get_patterns_pandas(cursor, level, mainMorphParams = None, depMorphParams = None, mainWordParam = None, depWordParam = None):
    where, params = create_where(True, mainMorphParams, depMorphParams, mainWordParam, depWordParam)
    comand = create_comand(level, where)
    cursor.execute(comand, params)
    res = cursor.fetchall()
    names = ['s_cl', 'animate', 'gender', 'number', 'case_morph', 'reflection', 'perfective', 'transitive', 'person', 'tense', 'voice', 'degree', 'static', 'prep_type']
    main_names = list(map(lambda x: 'main_' + x, names))
    dep_names = list(map(lambda x: 'dep_' + x, names))
    df = pd.DataFrame(res, columns = ['main_word', 'dep_word', 'mark'] + main_names + dep_names)
    for column in df.columns:
        if (df[column] == 'not_imp').all():
            df.drop(column, axis='columns', inplace=True)
    return df

def get_patterns(cursor, level, mainMorphParams = None, depMorphParams = None, mainWordParam = None, depWordParam = None):
    where, params = create_where(False, mainMorphParams, depMorphParams, mainWordParam, depWordParam)
    comand = create_comand(level, where)
    print(comand)
    print(params)
    cursor.execute(comand, params)
    res = cursor.fetchall()
    patternsList = []
    for pattern in res:
        mainConstr = []
        depConstr = []
        for i in range(3, NUMBER_PARAMETRS + 3):
            if pattern[i] != 'not_imp':
                mainConstr.append(pattern[i])
        for i in range(3 + NUMBER_PARAMETRS, 3 + 2 * NUMBER_PARAMETRS):
            if pattern[i] != 'not_imp':
                depConstr.append(pattern[i])
        newPattern = GPattern(level, pattern[0], pattern[1], pattern[2], \
                             mainConstr, depConstr)
        patternsList.append(newPattern)
    return patternsList