from Types import *
import psycopg2
import pandas as pd

def parseToMorph(text, curParse):
    curMorph = Morph()
    curMorph.probability = curParse.score
   # print(curParse)
   # print(curParse.tag)
    if (curParse.normal_form == "себя"):
        curMorph.s_cl = 'reflexivepronoun'
    elif (curParse.normal_form in ['я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они']):
        curMorph.s_cl = 'personalpronoun'
    elif ('Impe' in curParse.tag):
        curMorph.s_cl = 'unpersonalverb'
    elif ('Mult' in curParse.tag):
        curMorph.s_cl = 'frequentativeverb'
    elif ('Anum' in curParse.tag):
        curMorph.s_cl = 'numberordinal' # проверить!!!!
    elif (curParse.normal_form == "один"):
        curMorph.s_cl = 'numberone'
    elif (curParse.normal_form in ['два', 'оба', 'полтора']):
        curMorph.s_cl = 'numbertwo'
    elif (curParse.normal_form in ['три', 'четыре', 'сколько', 'несколько', 'столько', 'много', 'немного'] or 'Coll' in curParse.tag):
        curMorph.s_cl = 'numberthree'
    else:
        curMorph.s_cl = cl[str(curParse.tag.POS)]
    
    #print(curParse.tag.POS)#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    curMorph.animate = anim[str(curParse.tag.animacy)]
    if ("Ms-f" in curParse.tag):
        curMorph.gender = 'malefemale'
    else:
        curMorph.gender = gend[str(curParse.tag.gender)]
    curMorph.number = numb[str(curParse.tag.number)]
    if (str(curParse.tag.case) in cas):
        curMorph.case_morph = cas[str(curParse.tag.case)]
    else:
        print("wrong case", curParse.tag.case)
        return None
    #if 'Refl' in curMorph.tag:
    #    curMorph.Reflection = Ereflection.reflexive
    #как сделать reflexiveForm ??
    curCl = curParse.tag.POS
    if (curCl in ('VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'PRED')): #PRED -кат.сост. мб убрать
        if (text[-2:] == "ся"):
            if (curCl == 'VERB' or curCl == 'INFN'):
                curMorph.reflection = 'reflexive'
            else:
                curMorph.reflection = 'reflexive_form'
        else:
            curMorph.reflection = 'unreflexive'
    else:
        curMorph.reflection = 'reflection_any'
    curMorph.perfective = perf[str(curParse.tag.aspect)]
    curMorph.transitive = trans[str(curParse.tag.transitivity)]
    curMorph.person = pers[str(curParse.tag.person)]
    if (curCl == 'INFN'):
        curMorph.tense = 'infinitive'
    elif(curParse.tag.mood == 'impr'):
        curMorph.tense = 'imperative'
    else:
        curMorph.tense = tense[str(curParse.tag.tense)]
    curMorph.voice = voice[str(curParse.tag.voice)]
    #curMorph.degree =  ????????????????????????????????????????????????????????????????
    if (len(curParse.lexeme) == 1 or curMorph.s_cl == 'preposition' or curMorph.s_cl == 'gerund' or curMorph.s_cl == 'conjunction' or curMorph.s_cl == 'interjection' or curMorph.s_cl == 'adverb'): 
        curMorph.static = 'true'
    if curMorph.s_cl == 'preposition':
        if text in prepTypeDict.keys():
            curMorph.prep_type = prepTypeDict[text]
        else:
            print(text)
    return curMorph

def create_comand(level, where_str):
    if level == 1:
        return "select null, null, gp.mark, " + \
                "main.s_cl, main.animate, main.gender, main.number, main.case_morph, main.reflection, main.perfective, main.transitive, main.person, main.tense, main.voice, main.degree, main.static, main.prep_type, " + \
                 "dep.s_cl, dep.animate, dep.gender, dep.number, dep.case_morph, dep.reflection, dep.perfective, dep.transitive, dep.person, dep.tense, dep.voice, dep.degree, dep.static, dep.prep_type " + \
        "from gpattern_1_level as gp " + \
        "left join morph_constraints as main " + \
        "on main.id = main_morph " + \
        "left join morph_constraints as dep " + \
        "on dep.id = dep_morph " + \
        where_str + " order by mark desc"
    if level == 2:
        return "select main_word.name, null, gp.mark, " + \
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
    return "select main_word.name, dep_word.name, gp.mark, " + \
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