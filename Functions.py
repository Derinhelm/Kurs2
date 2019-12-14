from Types import *



def parseToMorph(text, curParse):
    curMorph = Morph()
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
    return curMorph

              
def findWord(word, db1, strForWord): # на выход - массив из номеров слов
#strForWord - дополнительная характеристика слова(главное, зависимое)
    s0 = "SELECT number_word, ref_to_morph FROM word WHERE word_text = \'" + word + "\';"
    variants = db1.query(s0)
    if (len(variants) > 1):
        print("Выберите варианты разбора " + strForWord + " слова  (указать номера в строку через пробел)\n")
        i = 0
        for i in range(len(variants)):
            curMorph = variants[i][1]
            curTextMorph = db1.query("SELECT * FROM morph_characters_of_word WHERE number_morph = " + str(curMorph))
            print(i)
            print(curTextMorph[0][1:])
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


def inputMorph(text = ""):
    print("Выберите характеристики" + text + " морфа\n")
    curMorph = Morph()
    for curEnum in Enums:
        j = 1
        for param in curEnum.__members__:
            print(j, sep = "", end = " - ")
            j += 1
            print(param)
        choose = int(input())
        print("---------------")
        curMorph.__dict__[curEnum.__name__[1:]] = curEnum(choose)
    print("static: 0 - True, 1 - False\n")
    choose = int(input())
    curMorph.static = (choose == 0)
    return curMorph

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
def insertWord(word, db1, morph1, insAllVars = False, listMorphs = None): # word - str
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
            curMorph = parseToMorph(word, pars[var])
            insertWordWithMorph(word, curMorph, pars[var].tag.cyr_repr, db1)   

def insertWordWithMorph(word, curMorph, tag, db1): # word - str
    # findMorph - получение номера морфа(один морф в идеале)
    numberMorph = findMorph(curMorph, db1)
    checkExist = db.query("SELECT * FROM word WHERE word_text = \'" + word + "\' AND " + "ref_to_morph = " + str(numberMorph) + ";")
    if (len(checkExist) == 0): # слова еще нет в базе
        s = "INSERT INTO word VALUES(DEFAULT, " + str(numberMorph) + ", \'" + word + "');"
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
            curMorph = parseToMorph(curLex.word, curLex)
            #print(curLex.tag)
            if (curMorph != None):
                insertWordWithMorph(curLex.word, curMorph, curLex.tag.cyr_repr, db1)
        #print("------------")
            


