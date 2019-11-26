import postgresql
from Types import *



def parseToMorf(text, curParse):
    curMorf = Morf()
   # print(curParse)
   # print(curParse.tag)
    if (curParse.normal_form == "себя"):
        curMorf.s_cl = 'reflexivepronoun'
    elif (curParse.normal_form in ['я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они']):
        curMorf.s_cl = 'personalpronoun'
    elif ('Impe' in curParse.tag):
        curMorf.s_cl = 'unpersonalverb'
    elif ('Mult' in curParse.tag):
        curMorf.s_cl = 'frequentativeverb'
    elif ('Anum' in curParse.tag):
        curMorf.s_cl = 'numberordinal' # проверить!!!!
    elif (curParse.normal_form == "один"):
        curMorf.s_cl = 'numberone'
    elif (curParse.normal_form in ['два', 'оба', 'полтора']):
        curMorf.s_cl = 'numbertwo'
    elif (curParse.normal_form in ['три', 'четыре', 'сколько', 'несколько', 'столько', 'много', 'немного'] or 'Coll' in curParse.tag):
        curMorf.s_cl = 'numberthree'
    else:
        curMorf.s_cl = cl[str(curParse.tag.POS)]
    
    #print(curParse.tag.POS)#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    curMorf.animate = anim[str(curParse.tag.animacy)]
    if ("Ms-f" in curParse.tag):
        curMorf.gender = 'malefemale'
    else:
        curMorf.gender = gend[str(curParse.tag.gender)]
    curMorf.number = numb[str(curParse.tag.number)]
    if (str(curParse.tag.case) in cas):
        curMorf.case1 = cas[str(curParse.tag.case)]
    else:
        print("wrong case", curParse.tag.case)
        return None
    #if 'Refl' in curMorf.tag:
    #    curMorf.Reflection = Ereflection.reflexive
    #как сделать reflexiveForm ??
    curCl = curParse.tag.POS
    if (curCl in ('VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'PRED')): #PRED -кат.сост. мб убрать
        if (text[-2:] == "ся"):
            if (curCl == 'VERB' or curCl == 'INFN'):
                curMorf.reflection = 'reflexive'
            else:
                curMorf.reflection = 'reflexive_form'
        else:
            curMorf.reflection = 'unreflexive'
    else:
        curMorf.reflection = 'reflection_any'
    curMorf.perfective = perf[str(curParse.tag.aspect)]
    curMorf.transitive = trans[str(curParse.tag.transitivity)]
    curMorf.person = pers[str(curParse.tag.person)]
    if (curCl == 'INFN'):
        curMorf.tense = 'infinitive'
    elif(curParse.tag.mood == 'impr'):
        curMorf.tense = 'imperative'
    else:
        curMorf.tense = tense[str(curParse.tag.tense)]
    curMorf.voice = voice[str(curParse.tag.voice)]
    #curMorf.degree =  ????????????????????????????????????????????????????????????????
    if (len(curParse.lexeme) == 1 or curMorf.s_cl == 'preposition' or curMorf.s_cl == 'gerund' or curMorf.s_cl == 'conjunction' or curMorf.s_cl == 'interjection' or curMorf.s_cl == 'adverb'): 
        curMorf.static = 'true'
    return curMorf

              
def findWord(word, db1, strForWord): # на выход - массив из номеров слов
#strForWord - дополнительная характеристика слова(главное, зависимое)
    s0 = "SELECT number_word, ref_to_morf FROM word WHERE word_text = \'" + word + "\';"
    variants = db1.query(s0)
    if (len(variants) > 1):
        print("Выберите варианты разбора " + strForWord + " слова  (указать номера в строку через пробел)\n")
        i = 0
        for i in range(len(variants)):
            curMorf = variants[i][1]
            curTextMorf = db1.query("SELECT * FROM morf_characters_of_word WHERE number_morf = " + str(curMorf))
            print(i)
            print(curTextMorf[0][1:])
            print("---------------------------")
        choose = list(map(int, input().split()))
    elif (len(variants) == 1):
        choose = [0]
    else:
        print("слова " + word + " нет в базе(добавить insertWord)")
        return []
    result = []
    for var in choose:
        if (var > len(variants)):
            print("неверный выбранный номер")
        else:
            result.append(variants[var][0])
    return result

def inputImpFeat(text): # text - главного/зависимого 
# на выход - массив из NUMBER_PARAMETRS true/false
    print("Выберите для данной модели важные свойства для " + text + " слова (укажите в строку через пробел)\n")
    for i in range(1, len(columns_imp_feat)):
        print(i - 1, columns_imp_feat[i][0])
    ans = list(map(int, input().split()))
    res = [False] * NUMBER_PARAMETRS
    for i in ans:
        res[i] = True
    return res


def inputMorf(text = ""):
    print("Выберите характеристики" + text + " морфа\n")
    curMorf = Morf()
    for curEnum in Enums:
        j = 1
        for param in curEnum.__members__:
            print(j, sep = "", end = " - ")
            j += 1
            print(param)
        choose = int(input())
        print("---------------")
        curMorf.__dict__[curEnum.__name__[1:]] = curEnum(choose)
    print("static: 0 - True, 1 - False\n")
    choose = int(input())
    curMorf.static = (choose == 0)
    return curMorf

def findPrep(prep, db1):
    s = "SELECT number_prep FROM prep WHERE prep_text = \'" + prep + "\'"
    res = db1.query(s)
    return res[0][0]

def findImp(curImp, db1): # на вход - вектор из NUMBER_PARAMETRS true/false
# на выход - одно число - номер imp_feat
    s = "SELECT number_imp_feat FROM important_features WHERE "
    #print(columns_imp_feat)
    for i in range(1, len(columns_imp_feat)):
        param = columns_imp_feat[i]
        prop = curImp[i - 1]
        s += (param[0] + "  = " + str(prop) + " ")
        if (i != len(columns_imp_feat) - 1):
            s += "AND "
    res = db.query(s)[0][0]
    return res    
def insertWord(word, db1, morph1, insAllVars = False, listMorfs = None): # word - str
    pars = morph1.parse(word)
    if (len(pars) > 1):
        if (insAllVars == True):
            choose = []
            for i in range(len(pars)):
                choose.append(i)
        else:
            print("Выберите варианты разбора слова " + word + " (указать номера в строку через пробел)")
            for i in range(len(pars)):
                print(i)
                print(pars[i].tag.cyr_repr)
                print("---------------") 
            choose = list(map(int, input().split()))
    else:
        choose = [0]
    for var in choose:
        if (var >= len(pars)):
            print(var, "неверный номер разбора\n", sep = " ")
        else:
            curMorf = parseToMorf(word, pars[var])
            insertWordWithMorf(word, curMorf, pars[var].tag.cyr_repr, db1)   

def insertWordWithMorf(word, curMorf, tag, db1): # word - str
    # findMorf - получение номера морфа(один морф в идеале)
    numberMorf = findMorf(curMorf, db1)
    checkExist = db.query("SELECT * FROM word WHERE word_text = \'" + word + "\' AND " + "ref_to_morf = " + str(numberMorf) + ";")
    if (len(checkExist) == 0): # слова еще нет в базе
        s = "INSERT INTO word VALUES(DEFAULT, " + str(numberMorf) + ", \'" + word + "');"
        db1.execute(s)
        #print("слово " + word + " в форме (" + str(tag) +") добавлено\n")
    #else:
        #print("слово " + word + " в форме (" + str(tag) + ") уже есть в базе\n")
        


def insertModel3(mainWord, depWord, prep, db1):
    numbMainWord = findWord(mainWord, db1, "главного") #массив номеров главного слова
    numbDepWord = findWord(depWord, db1, "зависимого") #массив номеров зависимого слова
    numbPrep = findPrep(prep, db1)
    for numbCurMain in numbMainWord:
        for numbCurDep in numbDepWord:
            impMain = inputImpFeat("главного")
            impDep = inputImpFeat("зависимого")
            numbImpMain = findImp(impMain, db1)
            numbImpDep = findImp(impDep, db1)
            end = "WHERE ref_to_main_word = " + str(numbCurMain) + \
            " AND ref_to_dep_word = " + str(numbCurDep) + " AND imp_feat_main = " + str(numbImpMain) + \
            " AND imp_feat_dep = " + str(numbImpDep) + " AND prep = " + str(numbPrep)
            s = "SELECT number_model FROM model_3_level " + end
            findUsedModel = db.query(s)#проверка, есть ли уже такая модель
            if (len(findUsedModel) == 0):
                s1 = "INSERT INTO model_3_level VALUES(DEFAULT, " + str(numbCurMain) + ", " + str(numbCurDep) + ", " + \
                str(numbImpMain) + ", " + str(numbImpDep) + ", " + str(numbPrep) + ", 1)"
                print("\nвставлено\n")
                db.execute(s1)
            else:
                s2 = "UPDATE model_3_level SET mark = mark + 1 " + end
                db.execute(s2)
                print("счетчик увеличен")

                
def insertParadigma(word, db1, morph1, insAllVars = False):
    pars = morph1.parse(word)
    normalForms = []
    parsForNormalForms = []
    for i in pars:
        curNorm = i.normal_form
        if (not (curNorm in normalForms)):
            normalForms.append(curNorm)
            parsForNormalForms.append(i)
    if (insAllVars == False):
        if (len(normalForms) > 1):
            print("Выберите варианты начальной формы слова " + word + " (указать номера в строку через пробел)")
            for i in range(len(normalForms)):
                print(i)
                print(normalForms[i])
                print(parsForNormalForms[i].tag)
                print("---------------") 
            choose = list(map(int, input().split()))
        else:
            choose = [0]
    else:
        choose = [i for i in range(0, len(normalForms))]
        #print(choose)
    for i in choose:
        for curLex in parsForNormalForms[i].lexeme:
            curMorf = parseToMorf(curLex.word, curLex)
            #print(curLex.tag)
            if (curMorf != None):
                insertWordWithMorf(curLex.word, curMorf, curLex.tag.cyr_repr, db1)
        #print("------------")
            


