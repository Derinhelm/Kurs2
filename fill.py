import copy
import pickle

import psycopg2
import pymorphy2

from dbFunctions import *
from functions import *

corporaToImpMorph = {'V': 's_cl', 'NUM': 's_cl', 'PR': 's_cl', 'A': 's_cl',
                     'ADV': 's_cl', 'CONJ': 's_cl', 'S': 's_cl', 'PART': 's_cl',
                     'ДЕЕПР': 's_cl', 'ПРИЧ': 's_cl', 'КР': 's_cl', 'СРАВ': 's_cl', 'INTJ': 's_cl',
                     'ПРЕВ': 's_cl',
                     'НЕОД': 'animate', 'ОД': 'animate',
                     'СРЕД': 'gender', 'МУЖ': 'gender', 'ЖЕН': 'gender',
                     'ЕД': 'number', 'МН': 'number',
                     'ИМ': 'case_morph', 'РОД': 'case_morph', 'ДАТ': 'case_morph',
                     'ВИН': 'case_morph', 'ТВОР': 'case_morph', 'ПР': 'case_morph', 'МЕСТН': 'case_morph',
                     'ПАРТ': 'case_morph',
                     'НЕСОВ': 'perfective', 'СОВ': 'perfective',
                     '3-Л': 'person', '2-Л': 'person', '1-Л': 'person',
                     'ПРОШ': 'tense', 'НАСТ': 'tense', 'НЕПРОШ': 'tense', 'ИНФ': 'tense',
                     'ИЗЪЯВ': 'tense', 'ПОВ': 'tense',
                     'СТРАД': 'voice'}


def parseCorporaTag(tagCorpora):
    # возвращает 1. список лямбда-функций, которые надо применить к морфу
    # для проверки на адекватность
    # 2. set важных параметров
    checkFuns = []
    impFeatures = set()
    for cur_param in tagCorpora:
        if cur_param == 'V':
            checkFuns.append(
                lambda m: m.s_cl in ['verb', 'participle', 'shortparticiple', 'gerund', 'frequentativeverb',
                                     'unpersonalverb', 'predicative'])
            impFeatures.add('transitive')
        elif cur_param == 'S':
            checkFuns.append(lambda m: m.s_cl in ['noun', 'pronoun', 'personalpronoun', 'name', 'pronounadjective',
                                                  'reflexivepronoun', 'comparative', 'predicative'])
        elif cur_param == 'A':
            checkFuns.append(
                lambda m: m.s_cl in ['adjective', 'shortadjective', 'number', 'pronoun', 'reflexivepronoun',
                                     'pronounadjective', 'possesiveadjective', 'comparative', 'predicative'])
        # прилагательное: новый, мой, второй
        elif cur_param == 'ADV':
            checkFuns.append(lambda m: m.s_cl in ['adverb', 'pronoun', 'comparative', 'predicative'])
        # наречие: плохо, отчасти
        elif cur_param == 'NUM':
            # числительное: пять, 2,
            checkFuns.append(lambda m: m.s_cl in ['number', 'numberordinal', 'numberone', 'numbertwo', 'numberthree',
                                                  'numberbiform'])
        elif cur_param == 'PR':
            checkFuns.append(lambda m: m.s_cl in ['preposition'])
            impFeatures.add('prep_type')
        # предлог: в, между, вопреки
        elif cur_param == 'CONJ':
            checkFuns.append(lambda m: m.s_cl in ['conjunction', 'pronoun'])
        # союз: и, что, как
        elif cur_param == 'PART':
            checkFuns.append(lambda m: m.s_cl in ['particle'])
        # частица: бы, ли, только
        elif cur_param == 'INTJ':
            checkFuns.append(lambda m: m.s_cl in ['interjection'])
        # междометие: ого, увы, эх
        elif cur_param == 'ИМ':
            checkFuns.append(lambda m: m.case_morph == 'nominative')
        elif cur_param == 'РОД':
            checkFuns.append(lambda m: m.case_morph == 'genitive')
        elif cur_param == 'ДАТ':
            checkFuns.append(lambda m: m.case_morph == 'dative')
        elif cur_param == 'ВИН':
            checkFuns.append(lambda m: m.case_morph == 'accusative')
        elif cur_param == 'ТВОР':
            checkFuns.append(lambda m: m.case_morph == 'instrumental')
        elif cur_param == 'ПР':
            checkFuns.append(lambda m: m.case_morph == 'prepositional')
        elif cur_param == 'ПАРТ':
            checkFuns.append(lambda m: m.case_morph == 'genitive')
        elif cur_param == 'МЕСТН':
            checkFuns.append(lambda m: m.case_morph == 'prepositional')
        elif cur_param == 'ЗВ':
            return [lambda m: False], None  # с звательным падежом пока не работаем

        elif cur_param == 'СРАВ':
            checkFuns.append(lambda m: m.s_cl == 'comparative')
        elif cur_param == 'КР':
            checkFuns.append(lambda m: m.s_cl == 'shortadjective' or m.s_cl == 'shortparticiple')
        elif cur_param == 'NID':
            return [lambda m: False], None

        elif cur_param == 'ЕД':
            checkFuns.append(lambda m: m.number == 'single')
        elif cur_param == 'МН':
            checkFuns.append(lambda m: m.number == 'plural')

        if cur_param not in ['СЛ', 'COM', 'СМЯГ', 'НЕСТАНД', 'МЕТА', 'НЕПРАВ']:
            impFeatures.add(corporaToImpMorph[cur_param])
    return checkFuns, impFeatures


def eqNormForm(s1, s2, parseS2):
    # равенство начальных форм слов
    # parseS2 - класс для превращения слова, разобранного в pymorphy2, в несов.вид
    if s1 == s2:
        return True
    if s1 == s2 + "ся":  # корпус убирает 'ся', pymorphy2 нет
        return True
    if s1.replace("ё", "е") == s2.replace("ё", "е"):
        return True
    s2Impf = parseS2.inflect({'INFN', 'impf'})
    if s2Impf is not None and parseS2.tag.POS == 'INFN' and s1 == s2Impf.word:
        # приводим второе слово в несов.вид
        # print(s1, s2)
        return True

    return False


# f = open('mismatch_of_the_initial_form', 'w')

def getParseByPymorphy(curWord, curTagCorpora, curNormalForm, arrParse):
    """return list of pairs (morph, normal form)"""
    (checkFuns, impFeatures) = parseCorporaTag(curTagCorpora)
    if impFeatures is None:  # слово типа NID, 'as-sifr'
        return []
    # print(curWord, curTagCorpora, curNormalForm, arrParse)
    notImpFeat = set(copy.copy(Morph.names)) - impFeatures
    goodParsePymorphy = []
    for cur_parse in arrParse:
        if eqNormForm(cur_parse.normal_form, curNormalForm, cur_parse) or \
                'НЕСТАНД' in curTagCorpora or 'НЕПРАВ' in curTagCorpora or \
                (('VERB' in cur_parse.tag or 'INFN' in cur_parse.tag or 'GRND' in cur_parse.tag or \
                  'PRTF' in cur_parse.tag or 'PRTS' in cur_parse.tag) and curTagCorpora[0] == 'V'):
            # для глаголов пока не требуем совпадения начальных форм
            m = Morph(cur_parse, curWord)
            nw = cur_parse.normal_form  # начальная форма слова
            if m is not None:
                flagTrueParse = True
                for curCheckFun in checkFuns:
                    if not curCheckFun(m):
                        flagTrueParse = False
                        break
                if flagTrueParse:
                    for curField in notImpFeat:
                        setattr(m, curField, 'not_imp')
                    if m not in goodParsePymorphy:
                        goodParsePymorphy += [(m, nw)]
    # else:
    # f.write(cur_parse.normal_form)
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


def insertPattern3(con, cursor, mainMorphNumber, depMorphNumber,
                   main_wordNumber, dep_wordNumber, mark):
    command = "SELECT id FROM gpattern_3_level WHERE " + \
              "main_morph = %s AND dep_morph = %s AND " + \
              "main_word = %s AND dep_word = %s;"
    params = (mainMorphNumber, depMorphNumber,
              main_wordNumber, dep_wordNumber)
    cursor.execute(command, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        command = "INSERT INTO gpattern_3_level " + \
                  "VALUES(DEFAULT, %s, %s, %s, %s, " + str(mark) + ");"
        cursor.execute(command, params)
    else:
        number_gpattern = ind[0][0]
        command = "UPDATE gpattern_3_level " + \
                  "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(command, (number_gpattern,))
    con.commit()


def insertPattern2(con, cursor, mainMorphNumber, depMorphNumber,
                   main_wordNumber, mark):
    command = "SELECT id FROM gpattern_2_level WHERE " + \
              "main_morph = %s AND dep_morph = %s AND " + \
              "main_word = %s;"
    params = (mainMorphNumber, depMorphNumber,
              main_wordNumber)
    cursor.execute(command, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        command = "INSERT INTO gpattern_2_level " + \
                  "VALUES(DEFAULT, %s, %s, %s, " + str(mark) + ");"
        cursor.execute(command, params)
    else:
        number_gpattern = ind[0][0]
        command = "UPDATE gpattern_2_level " + \
                  "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(command, (number_gpattern,))
    con.commit()


def insertPattern1(con, cursor, mainMorphNumber, depMorphNumber, mark):
    command = "SELECT id FROM gpattern_1_level WHERE " + \
              "main_morph = %s AND dep_morph = %s;"
    params = (mainMorphNumber, depMorphNumber)
    cursor.execute(command, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        command = "INSERT INTO gpattern_1_level " + \
                  "VALUES(DEFAULT, %s, %s, " + str(mark) + ");"
        cursor.execute(command, params)
    else:
        number_gpattern = ind[0][0]
        command = "UPDATE gpattern_1_level " + \
                  "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(command, (number_gpattern,))
    con.commit()


def insertPattern(con, cursor, mainMorphNumber, mainNormalFormNumber, depMorphNumber, depNormalFormNumber, mark):
    insertPattern3(con, cursor, mainMorphNumber, depMorphNumber,
                   mainNormalFormNumber, depNormalFormNumber, mark)
    insertPattern2(con, cursor, mainMorphNumber, depMorphNumber,
                   mainNormalFormNumber, mark)
    insertPattern1(con, cursor, mainMorphNumber, depMorphNumber, mark)


def insertAllPairs(con, cursor, mainInserts, depInserts):
    # массив номеров слова в таблице word(мб несколько в дальнейшем)
    # пока массив из одного элемента
    denominator = 0
    for cur_main in mainInserts:
        for cur_dep in depInserts:
            denominator += cur_main[2] * cur_dep[2]
    for cur_main in mainInserts:
        for cur_dep in depInserts:
            mainMorphNumber = cur_main[0]
            mainNormalFormNumber = cur_main[1]
            depMorphNumber = cur_dep[0]
            depNormalFormNumber = cur_dep[1]
            mark = cur_main[2] * cur_dep[2] / denominator
            insertPattern(con, cursor, mainMorphNumber, mainNormalFormNumber,
                          depMorphNumber, depNormalFormNumber, mark)


def check_word(word):
    if word is None:
        return False
    if word.count(" ") != 0:  # слова с пробелами пока не учитываем
        return False
    if '0' <= word[0] <= '9':
        return False
    return True


def insertPair(curPair, morph_analyzer: pymorphy2.MorphAnalyzer, con, cursor):
    (main_word, mainNormalForm, mainFeat, dep_word,
     depNormalForm, depFeat, _, _) = curPair
    if (not check_word(main_word)) or (not check_word(dep_word)):
        return
    depFeat = depFeat.split()
    mainFeat = mainFeat.split()
    depVariants = getParseByPymorphy(dep_word, depFeat, depNormalForm, morph_analyzer.parse(dep_word))
    mainVariants = getParseByPymorphy(main_word, mainFeat, mainNormalForm, morph_analyzer.parse(main_word))
    if depVariants == [] or mainVariants == []:
        return
    depVariants = deleteCPIFromList(depVariants)
    mainVariants = deleteCPIFromList(mainVariants)
    depVariantsNumbers = getNumberFromDB(depVariants, con, cursor)
    mainVariantsNumbers = getNumberFromDB(mainVariants, con, cursor)
    insertAllPairs(con, cursor, mainVariantsNumbers, depVariantsNumbers)


if __name__ == '__main__':
    # 610944- последняя сделанная
    morph_analyzer = pymorphy2.MorphAnalyzer()
    con = psycopg2.connect(dbname='gpatterns', user='postgres',
                           password='postgres', host='localhost')
    with open('pairsList.pickle', 'rb') as f:
        pairsList = pickle.load(f)
    for i in range(407785, len(pairsList)):
        print(i)
        curPair = pairsList[i]
        cursor = con.cursor()
        insertPair(curPair, morph_analyzer, con, cursor)
        cursor.close()
