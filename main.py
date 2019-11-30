import copy
from Types import *
from Functions import *
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import postgresql
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import write_dot, graphviz_layout

class GPattern:
    def __init__(self, l = -1, textWord = "", depWordConstr = None, p = "", m = 0.0):
        self.level = l
        self.dependentWord = textWord
        if (depWordConstr == None):
            self.dependentWordConstraints = []
        else:
            self.dependentWordConstraints = copy.deepcopy(depWordConstr)
        self.mark = m
        self.prep = p
        self.info = ""# ????


class GPatternList:
    def __init__(self):
        self.firstLevel = []
        self.secondLevel = []
        self.thirdLevel = []

def extractFirstLevel(word, curMorph, db):
    s1 = "SELECT number_morph FROM morph_characters_of_word WHERE " + \
        "s_cl = \'" + str(curMorph.s_cl).split('.')[1] + "\' AND " + \
        "animate = \'" + str(curMorph.animate).split('.')[1] + "\' AND " + \
        "gender = \'" + str(curMorph.gender).split('.')[1] + "\' AND " + \
        "number = \'" + str(curMorph.number).split('.')[1] + "\' AND " + \
        "case1 = \'" + str(curMorph.case1).split('.')[1] + "\' AND " + \
        "reflection = \'" + str(curMorph.reflection).split('.')[1] + "\' AND " + \
        "perfective = \'" + str(curMorph.perfective).split('.')[1] + "\' AND " + \
        "transitive = \'" + str(curMorph.transitive).split('.')[1] + "\' AND " + \
        "person = \'" + str(curMorph.person).split('.')[1] + "\' AND " + \
        "tense = \'" + str(curMorph.tense).split('.')[1] + "\' AND " + \
        "voice = \'" + str(curMorph.voice).split('.')[1] + "\' AND " + \
        "degree = \'" + str(curMorph.degree).split('.')[1] + "\' AND " + \
        "static = \'" + str(curMorph.static) + "\'"
    # s1 - получение номера морфа(один морф в идеале)
    s2 = "WITH morph AS (" + s1 + "), " + \
        "num_models AS (SELECT model_1_level.number_model FROM model_1_level, morph WHERE ref_to_main_morph = morph.number_morph), " + \
        "mod AS (SELECT model_1_level.* FROM model_1_level, num_models WHERE model_1_level.number_model = num_models.number_model), " + \
        "prop AS (SELECT number_model, morph_characters_of_word.* FROM mod, morph_characters_of_word WHERE mod.ref_to_dep_morph = morph_characters_of_word.number_morph), " + \
        "imp AS (SELECT number_model, important_features.* FROM mod, important_features WHERE mod.imp_feat_dep = important_features.number_imp_feat), " + \
        "pr AS (SELECT prep_text, number_model FROM prep, mod WHERE mod.prep = prep.number_prep) " + \
        "SELECT mod.mark, pr.prep_text, imp.*, prop.* FROM imp, prop, pr, mod WHERE imp.number_model = prop.number_model AND imp.number_model = mod.number_model AND pr.number_model = mod.number_model;"
    #print(s2)
    res = db.query(s2)
    firLev = []
    shiftImpFeat = 4
    shiftProp = 19
    #print(res)
    for curConstr in res:
        curPatt = GPattern(1)
        oneModelConstr = []
        for j in range(0, 13): #13 - количество свойств в Morph
            if (curConstr[shiftImpFeat + j] == True):
                oneModelConstr.append(curConstr[shiftProp + j])
        curPatt.dependentWordConstraints += oneModelConstr
        curPatt.mark = curConstr[0]
        curPatt.prep = curConstr[1]
        firLev.append(curPatt)
    #print(firLev)
    return firLev

def extractSecondLevel(word, curMorph, db):
    s0 = "SELECT number_morph FROM morph_characters_of_word WHERE " + \
        "s_cl = \'" + str(curMorph.s_cl).split('.')[1] + "\' AND " + \
        "animate = \'" + str(curMorph.animate).split('.')[1] + "\' AND " + \
        "gender = \'" + str(curMorph.gender).split('.')[1] + "\' AND " + \
        "number = \'" + str(curMorph.number).split('.')[1] + "\' AND " + \
        "case1 = \'" + str(curMorph.case1).split('.')[1] + "\' AND " + \
        "reflection = \'" + str(curMorph.reflection).split('.')[1] + "\' AND " + \
        "perfective = \'" + str(curMorph.perfective).split('.')[1] + "\' AND " + \
        "transitive = \'" + str(curMorph.transitive).split('.')[1] + "\' AND " + \
        "person = \'" + str(curMorph.person).split('.')[1] + "\' AND " + \
        "tense = \'" + str(curMorph.tense).split('.')[1] + "\' AND " + \
        "voice = \'" + str(curMorph.voice).split('.')[1] + "\' AND " + \
        "degree = \'" + str(curMorph.degree).split('.')[1] + "\' AND " + \
        "static = \'" + str(curMorph.static) + "\'"
    #получение морфа
    s1 = "WITH number_morph AS (" + s0 +"), number_word AS (SELECT number_word FROM word, number_morph  WHERE word.word_text = \'" + word + "\' AND word.ref_to_morph = number_morph.number_morph),"
    # s1 - получение номера главного слова(одно слово в идеале)
    s2 = s1 + \
    "mod AS (SELECT * FROM model_2_level, number_word WHERE model_2_level.ref_to_main_word = number_word.number_word), prop AS (SELECT number_model, morph_characters_of_word.* FROM mod, morph_characters_of_word WHERE mod.ref_to_dep_morph = morph_characters_of_word.number_morph), imp AS (SELECT number_model, important_features.* FROM mod, important_features WHERE mod.imp_feat_dep = important_features.number_imp_feat), pr AS (SELECT prep_text, number_model FROM prep, mod WHERE mod.prep = prep.number_prep) SELECT mod.mark, pr.prep_text, imp.*, prop.* FROM imp, prop, pr, mod WHERE imp.number_model = prop.number_model AND imp.number_model = mod.number_model AND pr.number_model = mod.number_model;"

    #print(s2)
    res = db.query(s2)
    secLev = []
    shiftImpFeat = 4
    shiftProp = 19
    #print(res)
    for curConstr in res:
        curPatt = GPattern(2)
        oneModelConstr = []
        for j in range(0, 13): #13 - количество свойств в Morph
            if (curConstr[shiftImpFeat + j] == True):
                oneModelConstr.append(curConstr[shiftProp + j])
        curPatt.dependentWordConstraints += oneModelConstr
        curPatt.mark = curConstr[0]
        curPatt.prep = curConstr[1]
        secLev.append(curPatt)
    #print(secLev)
    return secLev

def extractThirdLevel(word, curMorph, db):
    s0 = "SELECT number_morph FROM morph_characters_of_word WHERE " + \
        "s_cl = \'" + str(curMorph.s_cl).split('.')[1] + "\' AND " + \
        "animate = \'" + str(curMorph.animate).split('.')[1] + "\' AND " + \
        "gender = \'" + str(curMorph.gender).split('.')[1] + "\' AND " + \
        "number = \'" + str(curMorph.number).split('.')[1] + "\' AND " + \
        "case1 = \'" + str(curMorph.case1).split('.')[1] + "\' AND " + \
        "reflection = \'" + str(curMorph.reflection).split('.')[1] + "\' AND " + \
        "perfective = \'" + str(curMorph.perfective).split('.')[1] + "\' AND " + \
        "transitive = \'" + str(curMorph.transitive).split('.')[1] + "\' AND " + \
        "person = \'" + str(curMorph.person).split('.')[1] + "\' AND " + \
        "tense = \'" + str(curMorph.tense).split('.')[1] + "\' AND " + \
        "voice = \'" + str(curMorph.voice).split('.')[1] + "\' AND " + \
        "degree = \'" + str(curMorph.degree).split('.')[1] + "\' AND " + \
        "static = \'" + str(curMorph.static) + "\'"
    #получение морфа
    s1 = "WITH number_morph AS (" + s0 +"), number_word AS (SELECT number_word FROM word, number_morph  WHERE word.word_text = \'" + word + "\' AND word.ref_to_morph = number_morph.number_morph),"
    # s1 - получение номера главного слова(одно слово в идеале)
    s2 = s1 + \
    "mod AS (SELECT * FROM model_3_level, number_word WHERE model_3_level.ref_to_main_word = number_word.number_word), w AS (SELECT number_model, word.* FROM mod, word WHERE mod.ref_to_dep_word = word.number_word), imp AS (SELECT number_model, important_features.* FROM mod, important_features WHERE mod.imp_feat_dep = important_features.number_imp_feat), pr AS (SELECT prep_text, number_model FROM prep, mod WHERE mod.prep = prep.number_prep), prop AS (SELECT * FROM morph_characters_of_word, w WHERE morph_characters_of_word.number_morph = w.ref_to_morph) SELECT mod.mark, pr.prep_text, imp.*, prop.* FROM imp, w, pr, mod, prop WHERE imp.number_model = w.number_model AND imp.number_model = mod.number_model AND pr.number_model = mod.number_model AND prop.number_model = mod.number_model;"

    #print(s2)
    res = db.query(s2)
    thLev = []
    shiftImpFeat = 4
    shiftProp = 18
    #print(res)
    for curConstr in res:
        curPatt = GPattern(3)
        oneModelConstr = []
        for j in range(0, 13): #13 - количество свойств в Morph
            if (curConstr[shiftImpFeat + j] == True):
                oneModelConstr.append(curConstr[shiftProp + j])
        curPatt.dependentWordConstraints += oneModelConstr
        curPatt.mark = curConstr[0]
        curPatt.prep = curConstr[1]
        curPatt.dependentWord = curConstr[34]
        #print(curPatt.dependentWord)
        thLev.append(curPatt)
    #print(thLev)
    return thLev

class Word:
    def morphParse(self):
        p = morph.parse(self.word)
        for curParse in p:
            m = parseToMorph(self.word, curParse)
            self.morph.append(m)
            if (m.s_cl == Es_cl.preposition):
                self.canPrep = True

    def getGPatterns(self, db):
        for curMorph in self.morph:
            curPatt = GPatternList()
            curFirst = extractFirstLevel(self.word, curMorph, db)
            curSec = extractSecondLevel(self.word, curMorph, db)
            curThird = extractThirdLevel(self.word, curMorph, db)
            curPatt.firstLevel += curFirst
            curPatt.secondLevel += curSec
            curPatt.thirdLevel += curThird
            self.gPatterns.append(curPatt)

    def __init__(self, name = "", number = -1):
        self.word = name  # у Одинцева Word

        self.morph = []  # список объектов типа Morph

        # список морфологических характеристик для всех вариантов морф. анализа
        self.gPatterns = []  # список из GPatternList, i элемент - для i morph
        # с помощью морф.анализатора заполняем morph, с помощью базы - GPatterns
        self.canPrep = False # может ли слово быть использовано, как предлог
        self.numberInSentence = number

class Gp:
    def __init__(self):
        self.model = GPattern()
        self.depWord = Word()
        self.mark = 0
        self.level = 0

class ParsePointWord:
    def __init__(self):
        self.word = Word()
        self.parsed = False
        self.usedMorphAnswer = Morph()
        self.isUsedPrep = EUsedPrep.noPrep
        self.usedGp = []#типа Gp

class ParsePoint:
    directForIsApplicable = 1
    def __init__(self):
        self.parsePointWordList = []
        self.childParsePoint = []
    def getMark(self):
        summ = 0
        for curPointWord in self.parsePointWordList:
            if (curPointWord.parsed):
                summ += 0.01 # чтобы учитывать количество разобранных(важно, если одинаковые оценки, особенно 0)
                for curGp in curPointWord.usedGp:
                    summ += curGp.mark
        return summ

    def index(self, word1): # ищет в списке слов в данной точке разбора индекс данного слова(класса Word), вспомогательная функция
        for i in range(len(self.parsePointWordList)):
            if self.parsePointWordList[i].word == word1:
                return i
        return None
    
    def checkInderectDependency (self, numberMain, numberDep):
        depWord = self.parsePointWordList[numberDep]
        mainWord = self.parsePointWordList[numberMain]
        return True # ПЕРЕПИСАТЬ!!!!

    def checkIsWordInDependentGroup(self, numberMain, numberDep):
        return True # ПЕРЕПИСАТЬ!!!!!

    def checkMorph(self, morph, constraints):
        en = 0
        res = True
        for constr in range(len(constraints)):
            while (not (constraints[constr] in Enums[en]._member_names_)):
                en += 1
            nameEnum = Enums[en].__name__[1:].replace("case", "case1")
            if (str(morph.__dict__[nameEnum]) != Enums[en].__name__ + "." + constraints[constr]):
                res = False
                break
        return res

    def checkWord(self, depWord, gPattern): # на вход - потенциальное зависимое слово(или потенциальный предлог), модель управления
#  в какой морф.форме может быть зав.словом, None - не может быть
        constr = gPattern.dependentWordConstraints
        ans = 0
        if (gPattern.level == 3 and gPattern.dependentWord != depWord.word): # у 3 уровня не совпало слово
            return None
        for morph in depWord.morph:
            if (self.checkMorph(morph, constr)):
                return morph
        return None


    def rightMove(self, mainPPWord, gPatternToApply):
        numberUsedPrep = -1  # -1 - такого нет,  проверяем, что данный предлог встретился перед! зависимым словом Предполагаем, что данный предлог должен быть сама близким к зависимому из возможных
        # Шел с человеком с зонтом(человек с зонтом, т.к. иначе - непроективная конструкция) Важно, чтобы к зонту относилось второе с

        for numberDep in range(mainPPWord + 1, len(self.parsePointWordList),1):
            if (self.parsePointWordList[numberDep].parsed and self.parsePointWordList[numberDep].isUsedPrep == EUsedPrep.noPrep):
                if (self.checkInderectDependency(mainPPWord, numberDep) == False):
                    break
            else:
                depWord = self.parsePointWordList[numberDep].word
                morphForm = self.checkWord(depWord, gPatternToApply)
                if (morphForm != None and numberUsedPrep != -1 ):  # если уже был предлог, и данное i-слово удовлетворяет требованиям зависимости модели
                    return (True, numberUsedPrep, numberDep, morphForm)
                if (morphForm != None and gPatternToApply.prep == "None"):
                    return (True, None, numberDep, morphForm)
                if (depWord.canPrep and depWord.word == gPatternToApply.prep):
                    numberUsedPrep = numberDep #рассматриваемое слово может быть использовано, как предлог
        return (False, None, None, None)

    def leftMove(self, mainPPWord, gPatternToApply):
        # Шел с человеком с зонтом(человек с зонтом, т.к. иначе - непроективная конструкция) Важно, чтобы к зонту относилось второе с
# здесь сложнее, для каждого потенциального зависимого слова(которое уже подтвердили, что модель подходит), ищем, есть ли предлог слева..... - это тааак долго
        numbersPreps = [] # массив,в котором хранятся номера потенциальных предлогов(который нужен в модели управления )
        if (gPatternToApply.prep != "None"):
            for numberWord in range(0, mainPPWord):
                curWord = self.parsePointWordList[numberWord].word
                if (curWord.word == gPatternToApply.prep and curWord.canPrep):
                    numbersPreps.append(numberWord)
        for numberDep in range(mainPPWord - 1, -1 , -1):
            if (self.parsePointWordList[numberDep].parsed and self.parsePointWordList[numberDep].isUsedPrep == EUsedPrep.noPrep):
                if (self.checkInderectDependency(mainPPWord, numberDep) == False):
                    break
            else:
                depWord = self.parsePointWordList[numberDep].word
                morphForm = self.checkWord(depWord, gPatternToApply) # здесь нас не интересует maybePrep, т.к. предлог ищем слева
                if (morphForm != None):  # данное i-слово удовлетворяет требованиям зависимости модели
                    if (gPatternToApply.prep == "None"):
                        return (True, None, numberDep, morphForm)
                    if (numbersPreps[0] < numberDep): # есть предлоги(нужные) слева от потенц.зависимого
                        leftPrep = -1 # ищем самый правый из предлогов, которые слева от потенц.зависимого
                        for num in numbersPreps:
                            if (num < numberDep):
                                leftPrep = num
                            else:
                                break # Так как номера предлогов отсортированы по возрастанию
                        return (True, leftPrep, numberDep, morphForm)
        return (False, None, None, None)

    def isApplicable (self, mainPPWord, gPatternToApply): # где проверка предлогов???????
    #mainPPWord - номер главного!!!
        if (ParsePoint.directForIsApplicable > 0):
            (find, numberUsedPrep, numberDep, morphForm) = self.rightMove(mainPPWord, gPatternToApply)
            ParsePoint.directForIsApplicable = -ParsePoint.directForIsApplicable
            if (find):
                return (True, numberUsedPrep, numberDep, morphForm)
            return self.leftMove(mainPPWord, gPatternToApply)
        else:
            (find, numberUsedPrep, numberDep, morphForm) = self.leftMove(mainPPWord, gPatternToApply)
            ParsePoint.directForIsApplicable = -ParsePoint.directForIsApplicable
            if (find):
                return (True, numberUsedPrep, numberDep, morphForm)
            return self.rightMove(mainPPWord, gPatternToApply)



    def apply (self, mainPPWord, dependingPPWord, prepNumber, usedMorphAnswer, gPatternToApply):
        newParsePoint = copy.deepcopy(self)
        if (prepNumber != None):
            newParsePoint.parsePointWordList[prepNumber].parsed = True
            newParsePoint.parsePointWordList[prepNumber].isUsedPrep = EUsedPrep.usedPrep
        newParsePoint.parsePointWordList[dependingPPWord].parsed = True
        newParsePoint.parsePointWordList[dependingPPWord].usedMorphAnswer = usedMorphAnswer
        newGp = Gp()
        newGp.mark = gPatternToApply.mark
        newGp.level = gPatternToApply.level
        newGp.model = copy.deepcopy(gPatternToApply)
        newGp.depWord = self.parsePointWordList[dependingPPWord].word
        newParsePoint.parsePointWordList[mainPPWord].usedGp.append(newGp)
        return newParsePoint

    def getNextParsePoint(self): #(newPoint, flagFirstUse, firstWords)
        countParsed = 0
        parsed = []
        for i in range(len(self.parsePointWordList)):
            curPointWord = self.parsePointWordList[i]
            countParsed += curPointWord.parsed
            if (curPointWord.parsed == True):
                parsed.append(i)
        if (countParsed == 0):
            for i in range(len(self.parsePointWordList)):
                curPointWord = self.parsePointWordList[i]
                for curMorph in curPointWord.word.morph:
                    if curMorph.s_cl == Es_cl.verb:
                        newParsePoint = copy.deepcopy(self)
                        newParsePoint.parsePointWordList[i].parsed = True
                        newParsePoint.parsePointWordList[i].usedMorphAnswer = copy.deepcopy(curMorph)
                        self.childParsePoint.append(newParsePoint)
                        return (newParsePoint, True, [i]) # найдено первое для разбора слово
            #в предложении нет глагола
            for i in range(len(self.parsePointWordList)):
                curPointWord = self.parsePointWordList[i]
                for curMorph in curPointWord.word.morph:
                    if curMorph.s_cl == Es_cl.noun and curMorph.case1 == Ecase.nominative:
                        newParsePoint = copy.deepcopy(self)
                        newParsePoint.parsePointWordList[i].parsed = True
                        newParsePoint.parsePointWordList[i].usedMorphAnswer = copy.deepcopy(curMorph)
                        self.childParsePoint.append(newParsePoint)
                        return (newParsePoint, True, [i]) # найдено первое для разбора слово
        else:
            bestMainWord = Word()
            bestDepWord = Word()
            usedDepMorph = Morph()
            bestPrep = Word()
            bestModel = Gp()
            bestModelMark = 0
            for i in parsed:
                curParsedPoint = self.parsePointWordList[i]
                curWord = curParsedPoint.word
                chooseVarMorph = curParsedPoint.usedMorphAnswer
                models = None
                for j in range(len(curWord.morph)):
                    if (curWord.morph[j] == chooseVarMorph):
                        models = curWord.gPatterns[j]
                        break
                if (models != None):
                    for curModel in (models.thirdLevel + models.secondLevel + models.firstLevel):
                        (canApply, prep, depWord, morphDepWord) = self.isApplicable(i, curModel)
                        if (canApply and curModel.mark > bestModelMark): #!!!!!
                            bestPrep = prep
                            bestModelMark = curModel.mark
                            bestModel = copy.deepcopy(curModel)
                            bestMainWord = i
                            bestDepWord = depWord
                            usedDepMorph = morphDepWord
            if (bestModelMark != 0):
                newParsePoint = self.apply(bestMainWord, bestDepWord, bestPrep, usedDepMorph, bestModel)
                self.childParsePoint.append(newParsePoint)
                return (newParsePoint, False, None)
            print("No model")
            return (None, False, None)
        
        
    def addEdge(self, depth, newParsePointWordList, G1, shiftX, nameMainWord):
#добавляет в граф новую зависимую вершину и новую связь!
# beginIndex - строка, префикс названия 
# depth - глубина
#sList - исходное предложение - список слов
# shiftX - смещение по х всего блока точек,зависимых от данного
        for i in range(len(newParsePointWordList)):
            newParsePointWord = newParsePointWordList[i]
            newPointName = newParsePointWord.depWord.word
            G1.add_node(newPointName, pos = [shiftX + i * 9, 20 - 2 * depth])
            G1.add_edge(nameMainWord, newPointName)
            depWordText = newParsePointWord.depWord
            depWord1 = newParsePointWord.depWord
            depWordInd = depWord1.numberInSentence
            if (len(self.parsePointWordList[depWordInd].usedGp) != 0):
                self.addEdge(depth + 1, self.parsePointWordList[depWordInd].usedGp, G1, i * 7, newPointName)
    def visualizate(self, firstIndices):
        G1=nx.Graph()
        i = 0.5
        #for curWordParse in res.parsePointWordList:
        #    G1.add_node(curWordParse.word.word, pos = [i, 1])
        #    i += 4
        #for curPoint in parse1.usedGp:
        begin = firstIndices[0]
        parse1 = self.parsePointWordList[begin].usedGp
        textMainWord = self.parsePointWordList[begin].word.word
        max_x = 15
        max_y = 5.0
        # установить их потом!!!
        G1.add_node(textMainWord, pos = [5, 20])
        self.addEdge(1, parse1, G1, 0, textMainWord)
        pos=nx.get_node_attributes(G1,'pos')

        fig = plt.figure(figsize=(20,22))
        plt.scatter(max_x + 0.1, max_y + 0.1, s = 1, c = 'white')
        plt.scatter(-0.5, 0.0, s = 1, c = 'white')
        plt.scatter(max_x + 0.1, 0.0, s = 1, c = 'white')
        #pos=graphviz_layout(G1, prog='dot')
        nx.draw(G1, pos, with_labels = True, node_size=1, horizontalalignment='center', verticalalignment='top', font_size = 20)
class Sentence:
    def __init__(self):
        self.inputStr = ""
        self.wordList = []
        self.rootPP = ParsePoint()  # ????????
        self.firstUse = True
        self.firstParseWordsIndices = [] # слова, первые для разбора, в простых предложениях

    def setString(self, inputStr1):
        self.inputStr = inputStr1
        # слово в предложении - все, отделенное пробелом, точкой, ? ! ...(смотрим только на первую .)
        #: ; " ' началом предложения, запятой, (   ) тире вообще не учитываем(оно отделено пробелами),
        # дефис только в словах очень-очень и тп,
        punctuation = [' ', '.', '?', '!', ':', ';', '\'', '\"', ',', '(', ')']
        curWord = ""
        numberWord = 0
        for i in self.inputStr:
            if (i in punctuation):
                if (len(curWord) != 0):
                    self.wordList.append(Word(curWord.lower(), numberWord))
                    numberWord += 1
                    curWord = ""
            elif (i != '-' or (len(curWord) != 0)):  # - и непустое слово -  это дефис
                curWord = curWord + i
        if (len(curWord) != 0):
            self.wordList.append(Word(curWord.lower()), numberWord)


    def morphParse(self):
        for curWord in self.wordList:
            curWord.morphParse()

    def getGPatterns(self, db):
        for curWord in self.wordList:
            curWord.getGPatterns(db)

    def getRootParsePoint(self):
        self.rootPP = ParsePoint()
        for word in self.wordList:
            curParsePointWord = ParsePointWord()
            curParsePointWord.parsed = False
            curParsePointWord.word = word
            self.rootPP.parsePointWordList.append(curParsePointWord)
    def getBestParsePoint(self):
        bestPoint = self.rootPP
        bestPointMark = self.rootPP.getMark()
        for curChild in self.rootPP.childParsePoint:
            s1 = Sentence()
            s1.rootPP = curChild
            curBest = s1.getBestParsePoint()
            curMark = curBest.getMark()
            if (curMark > bestPointMark):
                bestPointMark = curMark
                bestPoint = curBest

        return bestPoint
    
# проверка связности - считаем, сколько слов в связном дереве, если = кол-ву слов, то все ок
# на вход - res(т.е. bestParsePoint)
    def countDependent(curParsePoint, firstWordIndex):
        newParsePointWord = curParsePoint.parsePointWordList[firstWordIndex]
        count = 1
        for curModel in newParsePointWord.usedGp:
            depWord1 = curModel.depWord
            print(depWord1.word)
            count +=  countDependent(curParsePoint, depWord1.numberInSentence)
        return count
    def checkConnectivity(self, curParsePoint): # параметр - предложение
        return len(self.wordList) == countDependent(curParsePoint, self.firstParseWordsIndices[0])
    
    def sintParse(self, needTrace = False):
        if (needTrace):
            tracePoints = []
        if (self.firstUse == True):
            self.firstUse = False
            self.getRootParsePoint()
        bestParsePoint = self.getBestParsePoint()
        if (bestParsePoint == None):
            print("Больше вариантов разбора нет")
            return None
        allWordsParsed = True
        
        for curPointWord in bestParsePoint.parsePointWordList:
            if (curPointWord.parsed == False):
                allWordsParsed = False
                break
        while (allWordsParsed == False):
            #for ti in range(len(bestParsePoint.parsePointWordList)):
            #    print(bestParsePoint.parsePointWordList[ti].parsed)
            #print("----------------")
            (newPoint, flagFirstUse, firstWords) = bestParsePoint.getNextParsePoint()
            if (newPoint == None):
                print("Не разобрано!")
                if (needTrace):
                    return (bestParsePoint, tracePoints)
                return (bestParsePoint)
            if (needTrace):
                tracePoints.append(newPoint)
            if (flagFirstUse):
                self.firstParseWordsIndices = firstWords
            s1 = Sentence()
            s1.rootPP = bestParsePoint# а надо ли copy ???
            bestParsePoint = s1.getBestParsePoint()
            allWordsParsed = True
            for curPointWord in bestParsePoint.parsePointWordList:
                if (curPointWord.parsed == False):
                    allWordsParsed = False
                    break
        if (needTrace):
            return (bestParsePoint, tracePoints)
        return (bestParsePoint)

def parse(db, str1, needTrace = False):
        s = Sentence()
        s.setString(str1)
        s.morphParse()
        s.getGPatterns(db)
        res = s.sintParse(needTrace)
        if (needTrace):
            res[0].visualizate(s.firstParseWordsIndices)
        else:
            res.visualizate(s.firstParseWordsIndices)
        return res
