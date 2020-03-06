import copy
import pickle

import psycopg2
import pymorphy2

from Functions import *
from dbFunctions import *

сorporaToImpMorph = {'V': 's_cl', 'NUM': 's_cl', 'PR': 's_cl', 'A': 's_cl', \
                     'ADV': 's_cl', 'CONJ': 's_cl', 'S': 's_cl', 'PART': 's_cl', \
                     'ДЕЕПР': 's_cl', 'ПРИЧ': 's_cl', 'КР': 's_cl', 'СРАВ': 's_cl', 'INTJ': 's_cl', \
                     'ПРЕВ': 's_cl', \
                     'НЕОД': 'animate', 'ОД': 'animate', \
                     'СРЕД': 'gender', 'МУЖ': 'gender', 'ЖЕН': 'gender', \
                     'ЕД': 'number', 'МН': 'number', \
                     'ИМ': 'case_morph', 'РОД': 'case_morph', 'ДАТ': 'case_morph', \
                     'ВИН': 'case_morph', 'ТВОР': 'case_morph', 'ПР': 'case_morph', 'МЕСТН': 'case_morph',
                     'ПАРТ': 'case_morph', \
                     'НЕСОВ': 'perfective', 'СОВ': 'perfective', \
                     '3-Л': 'person', '2-Л': 'person', '1-Л': 'person', \
                     'ПРОШ': 'tense', 'НАСТ': 'tense', 'НЕПРОШ': 'tense', 'ИНФ': 'tense', \
                     'ИЗЪЯВ': 'tense', 'ПОВ': 'tense', \
                     'СТРАД': 'voice'}


def parseCorporaTag(tagCorpora):
    # возвращает 1. список лямбда-функций, которые надо применить к морфу
    # для проверки на адекватность
    # 2. set важных параметров
    checkFuns = []
    impFeatures = set()
    for curParam in tagCorpora:
        # пока нет ниже 'comparative', 'predicative',
        if curParam == 'V':
            checkFuns.append(lambda m: m.s_cl in ['verb', 'participle', 'shortparticiple', 'gerund'])
            impFeatures.add('transitive')
        elif curParam == 'S':
            checkFuns.append(lambda m: m.s_cl in ['noun', 'pronoun'])
        elif curParam == 'A':
            checkFuns.append(lambda m: m.s_cl in ['adjective', 'shortadjective', 'number', 'pronoun'])
        # прилагательное: новый, мой, второй
        elif curParam == 'ADV':
            checkFuns.append(lambda m: m.s_cl in ['adverb', 'pronoun'])
        # наречие: плохо, отчасти
        elif curParam == 'NUM':
            # числительное: пять, 2,
            checkFuns.append(lambda m: m.s_cl in ['number'])
        elif curParam == 'PR':
            checkFuns.append(lambda m: m.s_cl in ['preposition'])
            impFeatures.add('prep_type')
        # предлог: в, между, вопреки
        elif curParam == 'CONJ':
            checkFuns.append(lambda m: m.s_cl in ['conjunction', 'pronoun'])
        # союз: и, что, как
        elif curParam == 'PART':
            checkFuns.append(lambda m: m.s_cl in ['particle'])
        # частица: бы, ли, только
        elif curParam == 'INTJ':
            checkFuns.append(lambda m: m.s_cl in ['interjection'])
        # междометие: ого, увы, эх
        elif curParam == 'ИМ':
            checkFuns.append(lambda m: m.case_morph == 'nominative')
        elif curParam == 'РОД':
            checkFuns.append(lambda m: m.case_morph == 'genitive')
        elif curParam == 'ДАТ':
            checkFuns.append(lambda m: m.case_morph == 'dative')
        elif curParam == 'ВИН':
            checkFuns.append(lambda m: m.case_morph == 'accusative')
        elif curParam == 'ТВОР':
            checkFuns.append(lambda m: m.case_morph == 'instrumental')
        elif curParam == 'ПР':
            checkFuns.append(lambda m: m.case_morph == 'prepositional')
        elif curParam == 'ПАРТ':
            checkFuns.append(lambda m: m.case_morph == 'genitive')
        elif curParam == 'МЕСТН':
            checkFuns.append(lambda m: m.case_morph == 'prepositional')
        elif curParam == 'ЗВ':
            return ([lambda m: False], None)  # с звательным падежом пока не работаем

        elif curParam == 'СРАВ':
            checkFuns.append(lambda m: m.s_cl == 'comparative')
        elif curParam == 'КР':
            checkFuns.append(lambda m: m.s_cl == 'shortadjective' or m.s_cl == 'shortparticiple')
        elif curParam == 'NID':
            return ([lambda m: False], None)

        elif curParam == 'ЕД':
            checkFuns.append(lambda m: m.number == 'single')
        elif curParam == 'МН':
            checkFuns.append(lambda m: m.number == 'plural')

        if not curParam in ['СЛ', 'COM', 'СМЯГ', 'НЕСТАНД', 'МЕТА', 'НЕПРАВ']:
            impFeatures.add(сorporaToImpMorph[curParam])
    return (checkFuns, impFeatures)


def eqNormForm(s1, s2, parseS2):
    # равенство начальных форм слов
    # parseS2 - класс для превращения слова, разобранного в pymorphy2, в несов.вид
    if s1 == s2:
        return True
    if (s1 == s2 + "ся"):  # корпус убирает 'ся', pymorphy2 нет
        return True
    if s1.replace("ё", "е") == s2.replace("ё", "е"):
        return True
    s2Impf = parseS2.inflect({'INFN', 'impf'})
    if s2Impf != None and parseS2.tag.POS == 'INFN' and s1 == s2Impf.word:
        # приводим второе слово в несов.вид
        # print(s1, s2)
        return True

    return False


# f = open('mismatch_of_the_initial_form', 'w')

def getParseByPymorphy(curWord, curTagCorpora, curNormalForm, arrParse):
    '''return list of pairs (morph, normal form)'''
    (checkFuns, impFeatures) = parseCorporaTag(curTagCorpora)
    if impFeatures == None:  # слово типа NID, 'as-sifr'
        return []
    # print(curWord, curTagCorpora, curNormalForm, arrParse)
    notImpFeat = set(copy.copy(Morph.names)) - impFeatures
    goodParsePymorphy = []
    for curParse in arrParse:
        if eqNormForm(curParse.normal_form, curNormalForm, curParse) or \
                'НЕСТАНД' in curTagCorpora or 'НЕПРАВ' in curTagCorpora or \
                (('VERB' in curParse.tag or 'INFN' in curParse.tag or 'GRND' in curParse.tag or \
                  'PRTF' in curParse.tag or 'PRTS' in curParse.tag) and curTagCorpora[0] == 'V'):
            # для глаголов пока не требуем совпадения начальных форм
            m = parseToMorph(curWord, curParse)
            nw = curParse.normal_form  # начальная форма слова
            if m != None:
                flagTrueParse = True
                for curCheckFun in checkFuns:
                    if not curCheckFun(m):
                        flagTrueParse = False
                        break
                if (flagTrueParse):
                    for curField in notImpFeat:
                        setattr(m, curField, 'not_imp')
                    if not m in goodParsePymorphy:
                        goodParsePymorphy += [(m, nw)]
    # else:
    # f.write(curParse.normal_form)
    # f.write("\n")
    # f.write(curNormalForm)
    # f.write("\n")
    # f.write("------------")
    # f.write("\n")
    return goodParsePymorphy


def deleteCPIFromList(variantsList):
    # не рассматриваем словосочетания с частицами, союзами и междометиями
    # variantsList - [(морф, начальная форма)]
    i = 0
    while i < len(variantsList):
        if variantsList[i][0].s_cl in ['conjunction', 'particle', 'interjection']:
            variantsList.pop(i)
        else:
            i += 1
    return variantsList


def getNumberFromDB(variantsList, con, cursor):
    # variantsList - список вида (морф, начальная форма)
    numbersList = []  # список вида (номер морфа, номер начальной формы)
    for curVariant in variantsList:
        (morph, normalForm) = curVariant
        morphNumber = str(findOrInsertMorph(con, morph, cursor))  # номер морфа в базе
        normalFormNumber = str(findOrInsertWord(con, normalForm, cursor))  # номер начальной формы в базе
        numbersList.append((morphNumber, normalFormNumber, morph.probability))
    return numbersList


def insertPattern3(con, cursor, mainMorphNumber, depMorphNumber, \
                   mainWordNumber, depWordNumber, mark):
    comand = "SELECT id FROM gpattern_3_level WHERE " + \
             "main_morph = %s AND dep_morph = %s AND " + \
             "main_word = %s AND dep_word = %s;"
    params = (mainMorphNumber, depMorphNumber, \
              mainWordNumber, depWordNumber)
    cursor.execute(comand, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        comand = "INSERT INTO gpattern_3_level " + \
                 "VALUES(DEFAULT, %s, %s, %s, %s, " + str(mark) + ");"
        cursor.execute(comand, params)
    else:
        number_gpattern = ind[0][0]
        comand = "UPDATE gpattern_3_level " + \
                 "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(comand, (number_gpattern,))
    con.commit()


def insertPattern2(con, cursor, mainMorphNumber, depMorphNumber, \
                   mainWordNumber, mark):
    comand = "SELECT id FROM gpattern_2_level WHERE " + \
             "main_morph = %s AND dep_morph = %s AND " + \
             "main_word = %s;"
    params = (mainMorphNumber, depMorphNumber, \
              mainWordNumber)
    cursor.execute(comand, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        comand = "INSERT INTO gpattern_2_level " + \
                 "VALUES(DEFAULT, %s, %s, %s, " + str(mark) + ");"
        cursor.execute(comand, params)
    else:
        number_gpattern = ind[0][0]
        comand = "UPDATE gpattern_2_level " + \
                 "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(comand, (number_gpattern,))
    con.commit()


def insertPattern1(con, cursor, mainMorphNumber, depMorphNumber, mark):
    comand = "SELECT id FROM gpattern_1_level WHERE " + \
             "main_morph = %s AND dep_morph = %s;"
    params = (mainMorphNumber, depMorphNumber)
    cursor.execute(comand, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        comand = "INSERT INTO gpattern_1_level " + \
                 "VALUES(DEFAULT, %s, %s, " + str(mark) + ");"
        cursor.execute(comand, params)
    else:
        number_gpattern = ind[0][0]
        comand = "UPDATE gpattern_1_level " + \
                 "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(comand, (number_gpattern,))
    con.commit()


def insertPattern(con, cursor, mainMorphNumber, mainNormalFormNumber, depMorphNumber, depNormalFormNumber, mark):
    insertPattern3(con, cursor, mainMorphNumber, depMorphNumber, \
                   mainNormalFormNumber, depNormalFormNumber, mark)
    insertPattern2(con, cursor, mainMorphNumber, depMorphNumber, \
                   mainNormalFormNumber, mark)
    insertPattern1(con, cursor, mainMorphNumber, depMorphNumber, mark)


def insertAllPairs(con, cursor, mainInserts, depInserts):
    # массив номеров слова в таблице word(мб несколько в дальнейшем)
    # пока массив из одного элемента
    denominator = 0
    for curMain in mainInserts:
        for curDep in depInserts:
            denominator += curMain[2] * curDep[2]
    for curMain in mainInserts:
        for curDep in depInserts:
            mainMorphNumber = curMain[0]
            mainNormalFormNumber = curMain[1]
            depMorphNumber = curDep[0]
            depNormalFormNumber = curDep[1]
            mark = curMain[2] * curDep[2] / denominator
            insertPattern(con, cursor, mainMorphNumber, mainNormalFormNumber, \
                          depMorphNumber, depNormalFormNumber, mark)


def checkWord(word):
    if word == None:
        return False
    if word.count(" ") != 0:  # слова с пробелами пока не учитываем
        return False
    if ('0' <= word[0] <= '9'):
        return False
    return True


def insertPair(curPair, morph, con, cursor):
    (mainWord, mainNormalForm, mainFeat, depWord,
     depNormalForm, depFeat, _, _) = curPair
    if (not checkWord(mainWord)) or (not checkWord(depWord)):
        return
    depFeat = depFeat.split()
    mainFeat = mainFeat.split()
    depVariants = getParseByPymorphy(depWord, depFeat, depNormalForm, morph.parse(depWord))
    mainVariants = getParseByPymorphy(mainWord, mainFeat, mainNormalForm, morph.parse(mainWord))
    if depVariants == [] or mainVariants == []:
        return
    depVariants = deleteCPIFromList(depVariants)
    mainVariants = deleteCPIFromList(mainVariants)
    depVariantsNumbers = getNumberFromDB(depVariants, con, cursor)
    mainVariantsNumbers = getNumberFromDB(mainVariants, con, cursor)
    insertAllPairs(con, cursor, mainVariantsNumbers, depVariantsNumbers)


morph = pymorphy2.MorphAnalyzer()
con = psycopg2.connect(dbname='gpatterns', user='postgres',
                       password='postgres', host='localhost')
with open('pairsList.pickle', 'rb') as f:
    pairsList = pickle.load(f)
for i in range(len(pairsList)):
    print(i)
    curPair = pairsList[i]
    cursor = con.cursor()
    insertPair(curPair, morph, con, cursor)
    cursor.close()
