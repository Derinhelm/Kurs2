import copy
from Types import *
from Functions import *
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import postgresql
import networkx as nx
import matplotlib.pyplot as plt

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
def extractFirstLevel(word, curMorf, db):
    s1 = "SELECT number_morf FROM morf_characters_of_word WHERE " + \
        "s_cl = \'" + str(curMorf.s_cl).split('.')[1] + "\' AND " + \
        "animate = \'" + str(curMorf.animate).split('.')[1] + "\' AND " + \
        "gender = \'" + str(curMorf.gender).split('.')[1] + "\' AND " + \
        "number = \'" + str(curMorf.number).split('.')[1] + "\' AND " + \
        "case1 = \'" + str(curMorf.case1).split('.')[1] + "\' AND " + \
        "reflection = \'" + str(curMorf.reflection).split('.')[1] + "\' AND " + \
        "perfective = \'" + str(curMorf.perfective).split('.')[1] + "\' AND " + \
        "transitive = \'" + str(curMorf.transitive).split('.')[1] + "\' AND " + \
        "person = \'" + str(curMorf.person).split('.')[1] + "\' AND " + \
        "tense = \'" + str(curMorf.tense).split('.')[1] + "\' AND " + \
        "voice = \'" + str(curMorf.voice).split('.')[1] + "\' AND " + \
        "degree = \'" + str(curMorf.degree).split('.')[1] + "\' AND " + \
        "static = \'" + str(curMorf.static) + "\'"
    # s1 - получение номера морфа(один морф в идеале)
    s2 = "WITH morf AS (" + s1 + "), " + \
        "num_models AS (SELECT model_1_level.number_model FROM model_1_level, morf WHERE ref_to_main_morf = morf.number_morf), " + \
        "mod AS (SELECT model_1_level.* FROM model_1_level, num_models WHERE model_1_level.number_model = num_models.number_model), " + \
        "prop AS (SELECT number_model, morf_characters_of_word.* FROM mod, morf_characters_of_word WHERE mod.ref_to_dep_morf = morf_characters_of_word.number_morf), " + \
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
        for j in range(0, 13): #13 - количество свойств в Morf
            if (curConstr[shiftImpFeat + j] == True):
                oneModelConstr.append(curConstr[shiftProp + j])
        curPatt.dependentWordConstraints += oneModelConstr
        curPatt.mark = curConstr[0]
        curPatt.prep = curConstr[1]
        firLev.append(curPatt)
    #print(firLev)
    return firLev

def extractSecondLevel(word, curMorf, db):
    s0 = "SELECT number_morf FROM morf_characters_of_word WHERE " + \
        "s_cl = \'" + str(curMorf.s_cl).split('.')[1] + "\' AND " + \
        "animate = \'" + str(curMorf.animate).split('.')[1] + "\' AND " + \
        "gender = \'" + str(curMorf.gender).split('.')[1] + "\' AND " + \
        "number = \'" + str(curMorf.number).split('.')[1] + "\' AND " + \
        "case1 = \'" + str(curMorf.case1).split('.')[1] + "\' AND " + \
        "reflection = \'" + str(curMorf.reflection).split('.')[1] + "\' AND " + \
        "perfective = \'" + str(curMorf.perfective).split('.')[1] + "\' AND " + \
        "transitive = \'" + str(curMorf.transitive).split('.')[1] + "\' AND " + \
        "person = \'" + str(curMorf.person).split('.')[1] + "\' AND " + \
        "tense = \'" + str(curMorf.tense).split('.')[1] + "\' AND " + \
        "voice = \'" + str(curMorf.voice).split('.')[1] + "\' AND " + \
        "degree = \'" + str(curMorf.degree).split('.')[1] + "\' AND " + \
        "static = \'" + str(curMorf.static) + "\'"
    #получение морфа
    s1 = "WITH number_morf AS (" + s0 +"), number_word AS (SELECT number_word FROM word, number_morf  WHERE word.word_text = \'" + word + "\' AND word.ref_to_morf = number_morf.number_morf),"
    # s1 - получение номера главного слова(одно слово в идеале)
    s2 = s1 + \
    "mod AS (SELECT * FROM model_2_level, number_word WHERE model_2_level.ref_to_main_word = number_word.number_word), prop AS (SELECT number_model, morf_characters_of_word.* FROM mod, morf_characters_of_word WHERE mod.ref_to_dep_morf = morf_characters_of_word.number_morf), imp AS (SELECT number_model, important_features.* FROM mod, important_features WHERE mod.imp_feat_dep = important_features.number_imp_feat), pr AS (SELECT prep_text, number_model FROM prep, mod WHERE mod.prep = prep.number_prep) SELECT mod.mark, pr.prep_text, imp.*, prop.* FROM imp, prop, pr, mod WHERE imp.number_model = prop.number_model AND imp.number_model = mod.number_model AND pr.number_model = mod.number_model;"

    #print(s2)
    res = db.query(s2)
    secLev = []
    shiftImpFeat = 4
    shiftProp = 19
    #print(res)
    for curConstr in res:
        curPatt = GPattern(2)
        oneModelConstr = []
        for j in range(0, 13): #13 - количество свойств в Morf
            if (curConstr[shiftImpFeat + j] == True):
                oneModelConstr.append(curConstr[shiftProp + j])
        curPatt.dependentWordConstraints += oneModelConstr
        curPatt.mark = curConstr[0]
        curPatt.prep = curConstr[1]
        secLev.append(curPatt)
    #print(secLev)
    return secLev

def extractThirdLevel(word, curMorf, db):
    s0 = "SELECT number_morf FROM morf_characters_of_word WHERE " + \
        "s_cl = \'" + str(curMorf.s_cl).split('.')[1] + "\' AND " + \
        "animate = \'" + str(curMorf.animate).split('.')[1] + "\' AND " + \
        "gender = \'" + str(curMorf.gender).split('.')[1] + "\' AND " + \
        "number = \'" + str(curMorf.number).split('.')[1] + "\' AND " + \
        "case1 = \'" + str(curMorf.case1).split('.')[1] + "\' AND " + \
        "reflection = \'" + str(curMorf.reflection).split('.')[1] + "\' AND " + \
        "perfective = \'" + str(curMorf.perfective).split('.')[1] + "\' AND " + \
        "transitive = \'" + str(curMorf.transitive).split('.')[1] + "\' AND " + \
        "person = \'" + str(curMorf.person).split('.')[1] + "\' AND " + \
        "tense = \'" + str(curMorf.tense).split('.')[1] + "\' AND " + \
        "voice = \'" + str(curMorf.voice).split('.')[1] + "\' AND " + \
        "degree = \'" + str(curMorf.degree).split('.')[1] + "\' AND " + \
        "static = \'" + str(curMorf.static) + "\'"
    #получение морфа
    s1 = "WITH number_morf AS (" + s0 +"), number_word AS (SELECT number_word FROM word, number_morf  WHERE word.word_text = \'" + word + "\' AND word.ref_to_morf = number_morf.number_morf),"
    # s1 - получение номера главного слова(одно слово в идеале)
    s2 = s1 + \
    "mod AS (SELECT * FROM model_3_level, number_word WHERE model_3_level.ref_to_main_word = number_word.number_word), w AS (SELECT number_model, word.* FROM mod, word WHERE mod.ref_to_dep_word = word.number_word), imp AS (SELECT number_model, important_features.* FROM mod, important_features WHERE mod.imp_feat_dep = important_features.number_imp_feat), pr AS (SELECT prep_text, number_model FROM prep, mod WHERE mod.prep = prep.number_prep), prop AS (SELECT * FROM morf_characters_of_word, w WHERE morf_characters_of_word.number_morf = w.ref_to_morf) SELECT mod.mark, pr.prep_text, imp.*, prop.* FROM imp, w, pr, mod, prop WHERE imp.number_model = w.number_model AND imp.number_model = mod.number_model AND pr.number_model = mod.number_model AND prop.number_model = mod.number_model;"

    #print(s2)
    res = db.query(s2)
    thLev = []
    shiftImpFeat = 4
    shiftProp = 18
    #print(res)
    for curConstr in res:
        curPatt = GPattern(3)
        oneModelConstr = []
        for j in range(0, 13): #13 - количество свойств в Morf
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
    def morfParse(self):
        p = morph.parse(self.word)
        for curParse in p:
            m = parseToMorf(self.word, curParse)
            self.morf.append(m)
            if (m.s_cl == Es_cl.preposition):
                self.canPrep = True

    def getGPatterns(self, db):
        for curMorf in self.morf:
            curPatt = GPatternList()
            curFirst = extractFirstLevel(self.word, curMorf, db)
            curSec = extractSecondLevel(self.word, curMorf, db)
            curThird = extractThirdLevel(self.word, curMorf, db)
            curPatt.firstLevel += curFirst
            curPatt.secondLevel += curSec
            curPatt.thirdLevel += curThird
            self.gPatterns.append(curPatt)

    def __init__(self, name=""):
        self.word = name  # у Одинцева Word

        self.morf = []  # список объектов типа Morf

        # список морфологических характеристик для всех вариантов морф. анализа
        self.gPatterns = []  # список из GPatternList, i элемент - для i morf
        # с помощью морф.анализатора заполняем morf, с помощью базы - GPatterns
        self.canPrep = False # может ли слово быть использовано, как предлог

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
        self.usedMorfAnswer = Morf()
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

    def checkInderectDependency (self, numberMain, numberDep):
        depWord = self.parsePointWordList[numberDep]
        mainWord = self.parsePointWordList[numberMain]
        return True # ПЕРЕПИСАТЬ!!!!

    def checkIsWordInDependentGroup(self, numberMain, numberDep):
        return True # ПЕРЕПИСАТЬ!!!!!

    def checkMorf(self, morf, constraints):
        en = 0
        res = True
        for constr in range(len(constraints)):
            while (not (constraints[constr] in Enums[en]._member_names_)):
                en += 1
            nameEnum = Enums[en].__name__[1:].replace("case", "case1")
            if (str(morf.__dict__[nameEnum]) != Enums[en].__name__ + "." + constraints[constr]):
                res = False
                break
        return res

    def checkWord(self, depWord, gPattern): # на вход - потенциальное зависимое слово(или потенциальный предлог), модель управления
#  в какой морф.форме может быть зав.словом, None - не может быть
        constr = gPattern.dependentWordConstraints
        ans = 0
        if (gPattern.level == 3 and gPattern.dependentWord != depWord.word): # у 3 уровня не совпало слово
            return None
        for morf in depWord.morf:
            if (self.checkMorf(morf, constr)):
                return morf
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
                morfForm = self.checkWord(depWord, gPatternToApply)
                if (morfForm != None and numberUsedPrep != -1 ):  # если уже был предлог, и данное i-слово удовлетворяет требованиям зависимости модели
                    return (True, numberUsedPrep, numberDep, morfForm)
                if (morfForm != None and gPatternToApply.prep == "None"):
                    return (True, None, numberDep, morfForm)
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
                morfForm = self.checkWord(depWord, gPatternToApply) # здесь нас не интересует maybePrep, т.к. предлог ищем слева
                if (morfForm != None):  # данное i-слово удовлетворяет требованиям зависимости модели
                    if (gPatternToApply.prep == "None"):
                        return (True, None, numberDep, morfForm)
                    if (numbersPreps[0] < numberDep): # есть предлоги(нужные) слева от потенц.зависимого
                        leftPrep = -1 # ищем самый правый из предлогов, которые слева от потенц.зависимого
                        for num in numbersPreps:
                            if (num < numberDep):
                                leftPrep = num
                            else:
                                break # Так как номера предлогов отсортированы по возрастанию
                        return (True, leftPrep, numberDep, morfForm)
        return (False, None, None, None)

    def isApplicable (self, mainPPWord, gPatternToApply): # где проверка предлогов???????
    #mainPPWord - номер главного!!!
        if (ParsePoint.directForIsApplicable > 0):
            (find, numberUsedPrep, numberDep, morfForm) = self.rightMove(mainPPWord, gPatternToApply)
            ParsePoint.directForIsApplicable = -ParsePoint.directForIsApplicable
            if (find):
                return (True, numberUsedPrep, numberDep, morfForm)
            return self.leftMove(mainPPWord, gPatternToApply)
        else:
            (find, numberUsedPrep, numberDep, morfForm) = self.leftMove(mainPPWord, gPatternToApply)
            ParsePoint.directForIsApplicable = -ParsePoint.directForIsApplicable
            if (find):
                return (True, numberUsedPrep, numberDep, morfForm)
            return self.rightMove(mainPPWord, gPatternToApply)



    def apply (self, mainPPWord, dependingPPWord, prepNumber, usedMorfAnswer, gPatternToApply):
        newParsePoint = copy.deepcopy(self)
        if (prepNumber != None):
            newParsePoint.parsePointWordList[prepNumber].parsed = True
            newParsePoint.parsePointWordList[prepNumber].isUsedPrep = EUsedPrep.usedPrep
        newParsePoint.parsePointWordList[dependingPPWord].parsed = True
        newParsePoint.parsePointWordList[dependingPPWord].usedMorfAnswer = usedMorfAnswer
        newGp = Gp()
        newGp.mark = gPatternToApply.mark
        newGp.level = gPatternToApply.level
        newGp.model = copy.deepcopy(gPatternToApply)
        newGp.depWord = self.parsePointWordList[dependingPPWord].word
        newParsePoint.parsePointWordList[mainPPWord].usedGp.append(newGp)
        return newParsePoint

    def getNextParsePoint(self):
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
                for curMorf in curPointWord.word.morf:
                    if curMorf.s_cl == Es_cl.verb:
                        newParsePoint = copy.deepcopy(self)
                        newParsePoint.parsePointWordList[i].parsed = True
                        newParsePoint.parsePointWordList[i].usedMorfAnswer = copy.deepcopy(curMorf)
                        self.childParsePoint.append(newParsePoint)
                        return newParsePoint

            #в предложении нет глагола
            for i in range(len(self.parsePointWordList)):
                curPointWord = self.parsePointWordList[i]
                for curMorf in curPointWord.word.morf:
                    if curMorf.s_cl == Es_cl.noun and curMorf.case1 == Ecase.nominative:
                        newParsePoint = copy.deepcopy(self)
                        newParsePoint.parsePointWordList[i].parsed = True
                        newParsePoint.parsePointWordList[i].usedMorfAnswer = copy.deepcopy(curMorf)
                        self.childParsePoint.append(newParsePoint)
                        return newParsePoint
        else:
            bestMainWord = Word()
            bestDepWord = Word()
            usedDepMorf = Morf()
            bestPrep = Word()
            bestModel = Gp()
            bestModelMark = 0
            for i in parsed:
                curParsedPoint = self.parsePointWordList[i]
                curWord = curParsedPoint.word
                chooseVarMorf = curParsedPoint.usedMorfAnswer
                models = None
                for j in range(len(curWord.morf)):
                    if (curWord.morf[j] == chooseVarMorf):
                        models = curWord.gPatterns[j]
                        break
                if (models != None):
                    for curModel in (models.thirdLevel + models.secondLevel + models.firstLevel):
                        (canApply, prep, depWord, morfDepWord) = self.isApplicable(i, curModel)
                        if (canApply and curModel.mark > bestModelMark): #!!!!!
                            bestPrep = prep
                            bestModelMark = curModel.mark
                            bestModel = copy.deepcopy(curModel)
                            bestMainWord = i
                            bestDepWord = depWord
                            usedDepMorf = morfDepWord
            if (bestModelMark != 0):
                newParsePoint = self.apply(bestMainWord, bestDepWord, bestPrep, usedDepMorf, bestModel)
                self.childParsePoint.append(newParsePoint)
                return newParsePoint
            print("No model")
            return None
    def visualizate(self):
        G1=nx.Graph()
        i = 0.5
        for curWordParse in self.parsePointWordList:
            G1.add_node(curWordParse.word.word, pos = [i, 1])
            i += 4
        max_x = i
        numberPoint = 1
        for curWordParse in self.parsePointWordList:
            mainWord = curWordParse.word.word
            for curPatt in curWordParse.usedGp:
                point = str(numberPoint)
                G1.add_node(point, pos = [numberPoint * 3 + 5, 5])
                G1.add_edge(point, mainWord)
                G1.add_edge(point, curPatt.depWord.word)
                if (curPatt.model.prep != "None"):
                    G1.add_edge(point, curPatt.model.prep)
                #print(mainWord, curPatt.depWord.word)
                #G1.add_edge("")
                #print(curPatt.depWord.word)
                numberPoint += 1
        pos=nx.get_node_attributes(G1,'pos')
        max_x = 15
        max_y = 5.0
        # установить их потом!!!

        fig = plt.figure(figsize=(20,5))
        plt.scatter(max_x + 0.1, max_y + 0.1, s = 1, c = 'white')
        plt.scatter(-0.5, 0.0, s = 1, c = 'white')
        plt.scatter(max_x + 0.1, 0.0, s = 1, c = 'white')
        nx.draw(G1, pos, with_labels = True, node_size=1, horizontalalignment='center', verticalalignment='top', font_size = 20)

class Sentence:
    def __init__(self):
        self.inputStr = ""
        self.wordList = []
        self.rootPP = ParsePoint()  # ????????
        self.firstUse = True

    def setString(self, inputStr1):
        self.inputStr = inputStr1
        # слово в предложении - все, отделенное пробелом, точкой, ? ! ...(смотрим только на первую .)
        #: ; " ' началом предложения, запятой, (   ) тире вообще не учитываем(оно отделено пробелами),
        # дефис только в словах очень-очень и тп,
        punctuation = [' ', '.', '?', '!', ':', ';', '\'', '\"', ',', '(', ')']
        curWord = ""
        for i in self.inputStr:
            if (i in punctuation):
                if (len(curWord) != 0):
                    self.wordList.append(Word(curWord.lower()))
                    curWord = ""
            elif (i != '-' or (len(curWord) != 0)):  # - и непустое слово -  это дефис
                curWord = curWord + i
        if (len(curWord) != 0):
            self.wordList.append(Word(curWord.lower()))
            curWord = ""

    def morfParse(self):
        for curWord in self.wordList:
            curWord.morfParse()

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
            newPoint = bestParsePoint.getNextParsePoint()
            if (newPoint == None):
                print("Не разобрано!")
                if (needTrace):
                    return (bestParsePoint, tracePoints)
                return (bestParsePoint)
            if (needTrace):
                tracePoints.append(newPoint)
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
        s.morfParse()
        s.getGPatterns(db)
        res = s.sintParse(needTrace)
        if (needTrace):
            res[0].visualizate()
        else:
            res.visualizate()
        return res
