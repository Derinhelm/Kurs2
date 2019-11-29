from Types import *
from Functions import *
from dbFunctions import *
import copy
import xml.dom.minidom
import pymorphy2
import psycopg2

class Node:
    def __init__(self, id1, dom1, feat1, text1, textNorm1, morphs1):
        self.id = id1
        self.dom = dom1
        self.feat = feat1
        self.text = text1
        self.textNorm = textNorm1
        self.arrMorphs = morphs1
        # список Morf, удовлетворяющих тегу корпуса

        # replace(".","") для сокращений
class Inserter:
    def __init__(self, mf, mt, df, dt):
        self.mainMorph = mf #список Morph
        self.mainText = mt
        self.depMorph = df #список Morph
        self.depText = dt
        self.count = 1
    def __eq__(self, other):
        return self.mainMorph == other.mainMorph and self.depMorph == other.depMorph and\
            self.mainText == other.mainText and self.depText == other.depText

morph = pymorphy2.MorphAnalyzer()
con = psycopg2.connect(dbname='gpatterns', user='postgres', 
                        password='postgres', host='localhost')

сorporaToImpMorph = {'V':'s_cl', 'NUM':'s_cl', 'PR':'s_cl', 'A':'s_cl', \
                   'ADV':'s_cl', 'CONJ':'s_cl', 'S':'s_cl', 'PART':'s_cl', \
                   'ДЕЕПР':'s_cl', 'ПРИЧ':'s_cl', 'КР':'s_cl', 'СРАВ':'s_cl', 'INTJ':'s_cl', \
                   'ПРЕВ':'s_cl', \
                   'НЕОД':'animate', 'ОД':'animate', \
                   'СРЕД':'gender', 'МУЖ':'gender', 'ЖЕН':'gender', \
                   'ЕД':'number', 'МН':'number', \
                   'ИМ':'case_morph', 'РОД':'case_morph', 'ДАТ':'case_morph', \
                   'ВИН':'case_morph', 'ТВОР':'case_morph', 'ПР':'case_morph', 'МЕСТН':'case_morph', 'ПАРТ':'case_morph', \
                   'НЕСОВ':'perfective', 'СОВ':'perfective', \
                   '3-Л':'person', '2-Л':'person', '1-Л':'person', \
                   'ПРОШ':'tense', 'НАСТ':'tense', 'НЕПРОШ':'tense', 'ИНФ':'tense', \
                   'ИЗЪЯВ':'tense', 'ПОВ':'tense', \
                   'СТРАД':'voice'}

def parseCorporaTag(tagCorpora):
    #возвращает 1. список лямбда-функций, которые надо применить к морфу
    #для проверки на адекватность
    # 2. set важных параметров
    checkFuns = []
    impFeatures = set()
    for curParam in tagCorpora:
        if curParam == 'СРАВ':
            checkFuns.append(lambda m: m.s_cl  == 'comparative')
        elif curParam == 'КР':
            checkFuns.append(lambda m: m.s_cl  == 'shortadjective' or m.s_cl == 'shortparticiple')
        elif curParam == 'NID':
            return ([lambda m: False], None)
        elif not curParam in ['СЛ', 'COM', 'СМЯГ', 'НЕСТАНД', 'МЕТА', 'НЕПРАВ']:
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
        #print(s1, s2)
        return True

    return False


def getParseByPymorphy(curWord, curTagCorpora, curNormalForm, arrParse):
    #print(curWord, curTagCorpora, curNormalForm, arrParse)
    isParsed = False  # был ли хоть один нормальный разбор
    (checkFuns, impFeatures) = parseCorporaTag(curTagCorpora)
    notImpFeat = copy.copy(Morf.names) - impFeatures
    goodParsePymorphy = []
    for curParse in arrParse:
        if eqNormForm(curParse.normal_form, curNormalForm, curParse) or \
                'НЕСТАНД' in curTagCorpora or 'НЕПРАВ' in curTagCorpora or \
                (('VERB' in curParse.tag or 'INFN' in curParse.tag) and curTagCorpora[0] == 'V'):
# для глаголов пока не требуем совпадения начальных форм
            m = parseToMorf(curWord, curParse)
            if m != None:
                flagTrueParse = True
                for curCheckFun in checkFuns:
                    if not curCheckFun(m):
                        flagTrueParse = False
                        break

                if (flagTrueParse):
                    isParsed = True
                    for curField in notImpFeat:
                        setattr(m, curField, 'not_imp')
                    if not m in goodParsePymorphy:
                        goodParsePymorphy += [m]
        if not isParsed:  # pymorphy2 не дал разбора, удовлетворяющего корпусу, пока не рассматриваем это слово
            #print("Разборы не соответствуют", curWord, curTagCorpora, curNormalForm)
            return None
    return goodParsePymorphy

def parseXML(nameFile, morph):
    doc = xml.dom.minidom.parse(nameFile)
    # а зачем храним id(на всякий случай), вообще-то можно и не хранить, id = index + 1
    arrayParseSentences = []
    parent = doc.getElementsByTagName('S')
    i = 1
    for item in parent:
        newSentence = []
        flagNormalWords = True # флаг отсутствия необычных слов(например, пропущенных и тп)
        #слов, у которых нет значения, т.е. элипсис и одно слово в Grechko.tgt
        for child in item.getElementsByTagName('W'):
            if len(child.childNodes) == 0:
                flagNormalWords = False
                print(i, word)
                break
#<W DOM="5" FEAT="V СОВ ИЗЪЯВ ПРОШ МН" ID="9" LEMMA="ОТВОДИТЬ" LINK="сочин" NODETYPE="FANTOM"/>
            else:
                (id1, dom, feat, word, normWord) =(child.getAttribute('ID'), child.getAttribute('DOM'), \
                           child.getAttribute('FEAT'), \
                           child.childNodes[0].nodeValue, child.getAttribute('LEMMA'))
                word = word.lower().replace("ё", "е").replace(".", "")
                normWord = normWord.lower().replace("ё", "е").replace(".", "")
                arrParse = morph.parse(word)
                realMorphs = getParseByPymorphy(word, feat.split(), normWord, arrParse)
                if realMorphs != None:
                    newNode = Node(id1, dom, feat, word, normWord, arrParse)
                    newSentence.append(newNode)
                else:
                    flagNormalWords = False
                    print(i, word)
                    break
        if flagNormalWords:
            arrayParseSentences.append(newSentence)
        i += 1
    return arrayParseSentences

def createInserters(nameFile, morph):
    arrayParseSentences = parseXML(nameFile, morph)
    #print(arrayParseSentences)
    manyInserter = []
    for curSentence in arrayParseSentences:
        for curWord in curSentence:
            flagNewInsert = False
            newArrInserter = []
            if curWord.dom != '_root':
                mainWord = curSentence[int(curWord.dom) - 1]
                # print(mainWord.text, curWord.text)
                newMainWord1 = mainWord
                newDepWord1 = curWord
                newInserter = Inserter(mainWord.arrMorphs, mainWord.text, \
                                       curWord.arrMorphs, curWord.text)
                flagNewInsert = True
                for curInserter in manyInserter:
                    if curInserter == newInserter:
                        curInserter.count += 1
                        break
                else:
                    manyInserter.append(newInserter)
    return manyInserter

manyInserter = createInserters("Algoritm.tgt", morph)