import copy
from Types import *
from Functions import *
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import psycopg2

class GPattern:
    def __init__(self, l = -1, textWord = "", nw = "", p = "", m = 0.0):
        self.level = l
        self.dependentWord = textWord
        self.dependentWordConstraints = [] # массив лямбда-функций ограничений на морф
        self.normalWord = nw
        self.mark = m
        self.info = ""# ????


class GPatternList:
    def __init__(self):
        self.firstLevel = []
        self.secondLevel = []
        self.thirdLevel = []


def extractFirstLevel(word, curMorph, con):
    s0 = "SELECT id FROM morph_constraints WHERE " + \
         "s_cl = %s AND " + \
         "(animate = %s OR animate = \'not_imp\') AND " + \
         "(gender = %s OR gender = \'not_imp\')  AND " + \
         "(number = %s OR number = \'not_imp\') AND " + \
         "(case_morph = %s OR case_morph = \'not_imp\') AND " + \
         "(reflection = %s OR reflection = \'not_imp\') AND " + \
         "(perfective = %s OR perfective = \'not_imp\') AND " + \
         "(transitive = %s OR transitive = \'not_imp\') AND " + \
         "(person = %s OR person = \'not_imp\') AND " + \
         "(tense = %s OR tense = \'not_imp\') AND " + \
         "(voice = %s OR voice = \'not_imp\') AND " + \
         "(degree = %s OR degree = \'not_imp\') AND " + \
         "(static = %s OR static = \'not_imp\')"

    # получение морфа
    # s1 - получение номера главного слова(одно слово в идеале)
    s2 = "SELECT * FROM gpattern_1_level WHERE main_morph IN (" + s0 + ")"
    s3 = "SELECT  mark, morph_constraints.* FROM (" + s2 + ") AS t JOIN morph_constraints ON morph_constraints.id = dep_morph;"
    cursor = con.cursor()
    params = (curMorph.s_cl, curMorph.animate, curMorph.gender, curMorph.number, \
              curMorph.case_morph, curMorph.reflection, curMorph.perfective, curMorph.transitive, \
              curMorph.person, curMorph.tense, curMorph.voice, curMorph.degree, curMorph.static)
    cursor.execute(s3, params)
    ans = cursor.fetchall()
    firLev = []
    for cur in ans:
        curPatt = GPattern(1)
        curConstr = []
        print("--------------")
        for j in range(2, 15):  # 13 - количество свойств в Morph
            if cur[j] != 'not_imp':
                curProp = Morph.names[j - 2]
                curConstr.append(((lambda m, cP, val: getattr(m, cP) == val), (curProp, cur[j])))
                print(curProp, cur[j])

        curPatt.dependentWordConstraints = curConstr
        curPatt.mark = cur[0]
        firLev.append(curPatt)
    cursor.close()
    return firLev

def extractSecondLevel(word, curMorph, con):
    s0 = "SELECT id FROM morph_constraints WHERE " + \
         "s_cl = %s AND " + \
         "(animate = %s OR animate = \'not_imp\') AND " + \
         "(gender = %s OR gender = \'not_imp\')  AND " + \
         "(number = %s OR number = \'not_imp\') AND " + \
         "(case_morph = %s OR case_morph = \'not_imp\') AND " + \
         "(reflection = %s OR reflection = \'not_imp\') AND " + \
         "(perfective = %s OR perfective = \'not_imp\') AND " + \
         "(transitive = %s OR transitive = \'not_imp\') AND " + \
         "(person = %s OR person = \'not_imp\') AND " + \
         "(tense = %s OR tense = \'not_imp\') AND " + \
         "(voice = %s OR voice = \'not_imp\') AND " + \
         "(degree = %s OR degree = \'not_imp\') AND " + \
         "(static = %s OR static = \'not_imp\')"

    # получение морфа
    # s1 - получение номера главного слова(одно слово в идеале)
    s2 = "SELECT * FROM gpattern_2_level WHERE main_morph IN (" + s0 + ") AND gpattern_2_level.main_word = " + \
        "(SELECT id FROM word WHERE name = %s)"
    s3 = "SELECT  mark, morph_constraints.* FROM (" + s2 + ") AS t JOIN morph_constraints ON morph_constraints.id = dep_morph;"
    cursor = con.cursor()
    params = (curMorph.s_cl, curMorph.animate, curMorph.gender, curMorph.number, \
              curMorph.case_morph, curMorph.reflection, curMorph.perfective, curMorph.transitive, \
              curMorph.person, curMorph.tense, curMorph.voice, curMorph.degree, curMorph.static, word)
    cursor.execute(s3, params)
    ans = cursor.fetchall()
    secLev = []
    for cur in ans:
        curPatt = GPattern(1)
        curConstr = []
        print("-------------")
        for j in range(2, 15):  # 13 - количество свойств в Morph
            if cur[j] != 'not_imp':
                curProp = Morph.names[j - 2]
                curConstr.append(((lambda m, cP, val: getattr(m, cP) == val), (curProp, cur[j])))
                print(curProp, cur[j])

        curPatt.dependentWordConstraints = curConstr
        curPatt.mark = cur[0]
        secLev.append(curPatt)
    cursor.close()
    return secLev

def extractThirdLevel(word, curMorph, con):
    s0 = "SELECT id FROM morph_constraints WHERE " + \
         "s_cl = %s AND " + \
         "(animate = %s OR animate = \'not_imp\') AND " + \
         "(gender = %s OR gender = \'not_imp\')  AND " + \
         "(number = %s OR number = \'not_imp\') AND " + \
         "(case_morph = %s OR case_morph = \'not_imp\') AND " + \
         "(reflection = %s OR reflection = \'not_imp\') AND " + \
         "(perfective = %s OR perfective = \'not_imp\') AND " + \
         "(transitive = %s OR transitive = \'not_imp\') AND " + \
         "(person = %s OR person = \'not_imp\') AND " + \
         "(tense = %s OR tense = \'not_imp\') AND " + \
         "(voice = %s OR voice = \'not_imp\') AND " + \
         "(degree = %s OR degree = \'not_imp\') AND " + \
         "(static = %s OR static = \'not_imp\')"

    # получение морфа
    # s1 - получение номера главного слова(одно слово в идеале)
    s2 = "SELECT * FROM gpattern_3_level WHERE main_morph IN (" + s0 + ") AND gpattern_3_level.main_word = " + \
        "(SELECT id FROM word WHERE name = %s)"
    s3 = "SELECT  mark, morph_constraints.*, word.name FROM (" + s2 + ") AS t JOIN morph_constraints ON morph_constraints.id = dep_morph " + \
    "JOIN word ON dep_word = word.id;"
    cursor = con.cursor()
    params = (curMorph.s_cl, curMorph.animate, curMorph.gender, curMorph.number, \
              curMorph.case_morph, curMorph.reflection, curMorph.perfective, curMorph.transitive, \
              curMorph.person, curMorph.tense, curMorph.voice, curMorph.degree, curMorph.static, word)
    cursor.execute(s3, params)
    ans = cursor.fetchall()
    thirdLev = []
    for cur in ans:
        curPatt = GPattern(1)
        curConstr = []
        print("-----------------")
        for j in range(2, 15):  # 13 - количество свойств в Morph
            if cur[j] != 'not_imp':
                curProp = Morph.names[j - 2]
                curConstr.append(((lambda m, cP, val: getattr(m, cP) == val), (curProp, cur[j])))
                print(curProp, cur[j])
        curPatt.normalWord = cur[15]
        curPatt.dependentWordConstraints = curConstr
        curPatt.mark = cur[0]
        thirdLev.append(curPatt)
    cursor.close()
    return thirdLev

class Word:
    def morphParse(self):
        p = morph.parse(self.word)
        for curParse in p:
            m = parseToMorph(self.word, curParse)
            self.morph.append(m)
            self.normalWord.append(curParse.normal_form)


    def getGPatterns(self, con):
        for i in range(len(self.morph)):
            curMorph = self.morph[i]
            curNormal = self.normalWord[i]
            curPatt = GPatternList()
            curFirst = extractFirstLevel(curNormal, curMorph, con)
            curSec = extractSecondLevel(curNormal, curMorph, con)
            curThird = extractThirdLevel(curNormal, curMorph, con)
            curPatt.firstLevel += curFirst
            curPatt.secondLevel += curSec
            curPatt.thirdLevel += curThird
            self.gPatterns.append(curPatt)

    def __init__(self, name = "", number = -1):
        self.word = name  # у Одинцева Word
        self.normalWord = [] # список начальных форм слов, соответствует morph(вместе заполняются)
        self.morph = []  # список объектов типа Morph

        # список морфологических характеристик для всех вариантов морф. анализа
        self.gPatterns = []  # список из GPatternList, i элемент - для i morph
        # с помощью морф.анализатора заполняем morph, с помощью базы - GPatterns
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
        for cur in constraints:
            curCheckFun = cur[0]
            curProperty = cur[1][0]
            val = cur[1][1]
            if not curCheckFun(morph, curProperty, val):
                return False
        return True

    def checkWord(self, depWord, gPattern): # на вход - потенциальное зависимое слово(или потенциальный предлог), модель управления
#  в какой морф.форме может быть зав.словом, None - не может быть
        constr = gPattern.dependentWordConstraints
        ans = 0
        for i in range(len(depWord.morph)):
            morph = depWord.morph[i]
            nw = depWord.normalWord[i]
            if gPattern.level != 3 or (gPattern.level == 3 and gPattern.normalWord == nw):
                if (self.checkMorph(morph, constr)):
                    return morph
        return None


    def rightMove(self, mainPPWord, gPatternToApply):

        for numberDep in range(mainPPWord + 1, len(self.parsePointWordList),1):
            if (self.parsePointWordList[numberDep].parsed):
                if (self.checkInderectDependency(mainPPWord, numberDep) == False):
                    break
            else:
                depWord = self.parsePointWordList[numberDep].word
                morphForm = self.checkWord(depWord, gPatternToApply)
                if (morphForm != None):
                    return (True, numberDep, morphForm)
        return (False, None, None)

    def leftMove(self, mainPPWord, gPatternToApply):
        # Шел с человеком с зонтом(человек с зонтом, т.к. иначе - непроективная конструкция) Важно, чтобы к зонту относилось второе с
# здесь сложнее, для каждого потенциального зависимого слова(которое уже подтвердили, что модель подходит), ищем, есть ли предлог слева..... - это тааак долго

        for numberDep in range(mainPPWord - 1, -1 , -1):
            if (self.parsePointWordList[numberDep].parsed):
                if (self.checkInderectDependency(mainPPWord, numberDep) == False):
                    break
            else:
                depWord = self.parsePointWordList[numberDep].word
                morphForm = self.checkWord(depWord, gPatternToApply)
                if (morphForm != None):  # данное i-слово удовлетворяет требованиям зависимости модели
                    return (True, numberDep, morphForm)
        return (False, None, None)
        return (False, None, None)

    def isApplicable (self, mainPPWord, gPatternToApply): # где проверка предлогов???????
    #mainPPWord - номер главного!!!
        if (ParsePoint.directForIsApplicable > 0):
            (find, numberDep, morphForm) = self.rightMove(mainPPWord, gPatternToApply)
            ParsePoint.directForIsApplicable = -ParsePoint.directForIsApplicable
            if (find):
                return (True, numberDep, morphForm)
            return self.leftMove(mainPPWord, gPatternToApply)
        else:
            (find, numberDep, morphForm) = self.leftMove(mainPPWord, gPatternToApply)
            ParsePoint.directForIsApplicable = -ParsePoint.directForIsApplicable
            if (find):
                return (True, numberDep, morphForm)
            return self.rightMove(mainPPWord, gPatternToApply)



    def apply (self, mainPPWord, dependingPPWord, usedMorphAnswer, gPatternToApply):
        newParsePoint = copy.deepcopy(self)
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
                    if curMorph.s_cl == 'verb':
                        newParsePoint = copy.deepcopy(self)
                        newParsePoint.parsePointWordList[i].parsed = True
                        newParsePoint.parsePointWordList[i].usedMorphAnswer = copy.deepcopy(curMorph)
                        self.childParsePoint.append(newParsePoint)
                        return (newParsePoint, True, [i]) # найдено первое для разбора слово
            #в предложении нет глагола
            for i in range(len(self.parsePointWordList)):
                curPointWord = self.parsePointWordList[i]
                for curMorph in curPointWord.word.morph:
                    if curMorph.s_cl == 'noun' and curMorph.case_morph == 'nominative':
                        newParsePoint = copy.deepcopy(self)
                        newParsePoint.parsePointWordList[i].parsed = True
                        newParsePoint.parsePointWordList[i].usedMorphAnswer = copy.deepcopy(curMorph)
                        self.childParsePoint.append(newParsePoint)
                        return (newParsePoint, True, [i]) # найдено первое для разбора слово
        else:
            bestMainWord = Word()
            bestDepWord = Word()
            usedDepMorph = Morph()
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
                        (canApply, depWord, morphDepWord) = self.isApplicable(i, curModel)
                        if (canApply and curModel.mark > bestModelMark): #!!!!!
                            bestModelMark = curModel.mark
                            bestModel = copy.deepcopy(curModel)
                            bestMainWord = i
                            bestDepWord = depWord
                            usedDepMorph = morphDepWord
            if (bestModelMark != 0):
                newParsePoint = self.apply(bestMainWord, bestDepWord, usedDepMorph, bestModel)
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
        nx.draw(G1, pos, with_labels = True, arrows=False, node_size=1, horizontalalignment='center', verticalalignment='top', font_size = 20)
        plt.show()
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

    def getGPatterns(self, con):
        for curWord in self.wordList:
            curWord.getGPatterns(con)

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
    def countDependent(self, curParsePoint, firstWordIndex):
        newParsePointWord = curParsePoint.parsePointWordList[firstWordIndex]
        count = 1
        for curModel in newParsePointWord.usedGp:
            depWord1 = curModel.depWord
            print(depWord1.word)
            count += self.countDependent(curParsePoint, depWord1.numberInSentence)
        return count
    def checkConnectivity(self, curParsePoint): # параметр - предложение
        return len(self.wordList) == self.countDependent(curParsePoint, self.firstParseWordsIndices[0])
    
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

def parse(con, str1, needTrace = False):
        s = Sentence()
        s.setString(str1)
        s.morphParse()
        s.getGPatterns(con)
        res = s.sintParse(needTrace)
        if (needTrace):
            res[0].visualizate(s.firstParseWordsIndices)
        else:
            res.visualizate(s.firstParseWordsIndices)
        return res

con = psycopg2.connect(dbname='gpatterns', user='postgres',
                        password='postgres', host='localhost')


a1 = parse(con, "Маленький мальчик хочет спать.", True)
a1 = parse(con, "Каждый час имеет свое чудо.", True)
a1 = parse(con, "Памятник себе воздвиг нерукотворный.", True)
a1 = parse(con, "Рассеет серых туч войска.", True)
#a1 = parse(con, "Сегодня будет четный день.", True)
a1 = parse(con, "Шекспир был английским писателем.", True)
a1 = parse(con, "Надежда умирает последней.", True)
a1 = parse(con, "В небе танцует золото.", True)
a1 = parse(con, "Звезды.", True)




#a1 = parse(con, "Взрослые люди ходят на работу.", True)

#a1 = parse(con, "Приведет за собой весну.", True) плохо
#a1 = parse(con, "Взрослые люди ходят на работу.", True) плохо
#a1 = parse(con, "Заяц поздней осенью меняет серую шубу на белую.", True)
#a1 = parse(con, "Я прочел до середины список кораблей.", True)
#a1 = parse(con, "Вязнут расписные спицы в расхлябанные колеи.", True)
#a1 = parse(con, "Ковыли с вековою тоскою пригнулись к земле.", True)
#a1 = parse(con, "К метро шли долго.", True)
#a1 = parse(con, "Студенты замерзли на лекции.", True)
#a1 = parse(con, "Ты стал очень хорошим человеком.", True)


#a1 = parse(con, "Ты будешь сок?", True)
#a1 = parse(con, "Все счастливые семьи счастливы по-своему.", True)
#a1 = parse(con, "Осень поражает нас своими непрерывными изменениями.", True)
#a1 = parse(con, "Вещи, потерянные нами, обязательно вернутся к нам!.", True)




#a1 = parse(con, "Моя ладонь превратилась в кулак.", True) плохо

#a1 = parse(con, "Счастье можно найти даже в темные времена.", True) плохо

#a1 = parse(con, "Дети поздно пришли домой.", True)  плохо
#a1 = parse(con, "На штурм.", True)  плохо главное дб НА

print(a1)