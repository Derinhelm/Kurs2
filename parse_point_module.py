from Functions import get_patterns
from Types import parseToMorph
import copy
from Attempts_module import Attempts
import networkx as nx

class WordForm:
    def __init__(self, con, morph, normal_form):
        self.normal_form = normal_form
        self.morph = morph
        self.g_patterns = [] #список из Gpattern, в которых данная словоформа мб главной
        self.create_patterns(con)

    def __repr__(self):
        return self.normal_form + " " + self.morph.__repr__()

    def create_patterns(self, con):
        cursor = con.cursor()
        morph_constr = self.morph.get_imp()
        cur_first = get_patterns(cursor, 1, mainMorphParams = morph_constr)
        cur_sec = get_patterns(cursor, 2, mainMorphParams = morph_constr, mainWordParam = self.normal_form)
        cur_third = get_patterns(cursor, 3, mainMorphParams = morph_constr, mainWordParam = self.normal_form)
        cursor.close()
        self.g_patterns += cur_third
        self.g_patterns += cur_sec
        self.g_patterns += cur_first
        return
    def get_patterns(self):
        return self.g_patterns

class Word:
    def __init__(self, con, morph, word_text, number=-1):
        self.word_text = word_text
        self.forms = []
        self.numberInSentence = number
        self.morphParse(con, morph)
# toDo numberInSentence убрать

    def morphParse(self, con, morph):
        if self.word_text[-1] == '.':
            p = morph.parse(self.word_text[:-1])
            abbr = True
        else:
            p = morph.parse(self.word_text)
            abbr = False
        for curParse in p:
            if (abbr and 'Abbr' in curParse.tag) or \
                    (not abbr and not 'Abbr' in curParse.tag):
            # чтобы предлогу "к" не приписывался вариант кандидат
                morph = parseToMorph(self.word_text, curParse)
                cur_form = WordForm(con, morph, curParse.normal_form)
                self.forms.append(cur_form)
        return

    def get_all_form_patterns(self):
        return [form.g_patterns for form in self.forms]

class Gp:
    def __init__(self, mod, dw):
        self.model = mod
        self.depWord = dw


class ParsePointWord:
    def __init__(self, word):
        self.word = word
        self.parsed = False
        self.usedMorphAnswer = None# типа WordForm
        self.usedGp = []  # типа Gp


class ParsePoint:
    directForIsApplicable = 1

    def __init__(self, ppwl, cl, mark, cpw, par, num, att, g):
        self.parsePointWordList = ppwl
        self.childParsePoint = cl
        self.markParsePoint = mark
        self.countParsedWords = cpw
        self.parsed = par
        self.numberPoint = num
        self.attempts = att
        self.graph = g# хранится граф (networkx)

    def __repr__(self):
        ans = str(self.numberPoint) + ":"
        for i in self.parsed:
            ans += str(i[0]) + "+" + str(i[1]) + ";"
        return ans

    def getMark(self, parentMark):
        '''return mark of ParsePoint and count of parsed word in this ParsePoint'''
        summ = 0
        countParsedWord = 0
        for curPointWord in self.parsePointWordList:
            if (curPointWord.parsed):
                countParsedWord += 1
                for curGp in curPointWord.usedGp:
                    summ += curGp.model.mark # toDO  был log, а нам вообще нужны оценки точек разбора?
        return ((summ + parentMark), countParsedWord)

    def index(self,
              word1):  # ищет в списке слов в данной точке разбора индекс данного слова(класса Word), вспомогательная функция
        for i in range(len(self.parsePointWordList)):
            if self.parsePointWordList[i].word == word1:
                return i
        return None

    def checkInderectDependency(self, numberMain, numberDep):
        depWord = self.parsePointWordList[numberDep]
        mainWord = self.parsePointWordList[numberMain]
        return True  # ПЕРЕПИСАТЬ!!!!

    def checkIsWordInDependentGroup(self, numberMain, numberDep):
        return True  # ПЕРЕПИСАТЬ!!!!!

    def checkMorph(self, morph, constraints):
        for cur in constraints:
            curCheckFun = cur[0]
            curProperty = cur[1][0]
            val = cur[1][1]
            if not curCheckFun(morph, curProperty, val):
                return False
        return True

    def rightMove(self, mainPPWord, gPatternToApply):

        for numberDep in range(mainPPWord + 1, len(self.parsePointWordList), 1):
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

        for numberDep in range(mainPPWord - 1, -1, -1):
            if (self.parsePointWordList[numberDep].parsed):
                if (self.checkInderectDependency(mainPPWord, numberDep) == False):
                    break
            else:
                depWord = self.parsePointWordList[numberDep].word
                morphForm = self.checkWord(depWord, gPatternToApply)
                if (morphForm != None):  # данное i-слово удовлетворяет требованиям зависимости модели
                    return (True, numberDep, morphForm)
        return (False, None, None)

    def isApplicable(self, mainPPWord, gPatternToApply):  # где проверка предлогов???????
        # mainPPWord - номер главного!!!
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

    def apply(self, mainPPWord, dependingPPWord, usedMorphAnswer, gPatternToApply, maxNumberPoint):
        '''create and return new child ParsePoint'''
        new_word_list = copy.deepcopy(self.parsePointWordList)
        new_word_list[dependingPPWord].parsed = True
        new_word_list[dependingPPWord].usedMorphAnswer = usedMorphAnswer
        newGp = Gp(gPatternToApply, self.parsePointWordList[dependingPPWord].word)
        new_word_list[mainPPWord].usedGp.append(newGp)
        newMark = self.markParsePoint + gPatternToApply.mark
        newParsedList = copy.deepcopy(self.parsed)
        newParsedList.append((mainPPWord, dependingPPWord))
        newNumber = maxNumberPoint + 1
        newAttempts = copy.deepcopy(self.attempts)
        newAttempts.apply()
        newGraph = copy.deepcopy(self.graph)
        depWord = self.parsePointWordList[dependingPPWord].word.word_text + "_" + str(dependingPPWord)
        mainWord = self.parsePointWordList[mainPPWord].word.word_text + "_" + str(mainPPWord)
        newGraph.add_node(depWord)
        newGraph.add_edge(mainWord, depWord)
        return ParsePoint(new_word_list, [], newMark, self.countParsedWords + 1, newParsedList, newNumber, newAttempts, newGraph)

    def find_first_word(self, fun, listNumbersVariants, allPatternsListParam, morphPosition, wordPosition):
        numberChildPoint = self.numberPoint + 1
        for i in range(len(self.parsePointWordList)):
            curPointWord = self.parsePointWordList[i]
            listNewParsePoints = []
            for j in range(len(curPointWord.word.forms)):
                curMorph = curPointWord.word.forms[j].morph
                if fun(curMorph):
                    new_word_list = copy.deepcopy(self.parsePointWordList)
                    new_word_list[i].parsed = True
                    new_word_list[i].usedMorphAnswer = copy.deepcopy(curPointWord.word.forms[j])
                    curListNumberVariants = copy.deepcopy(listNumbersVariants)
                    patternsCurVariant = new_word_list[i].word.forms[j].g_patterns
                    att = Attempts(i, patternsCurVariant, curListNumberVariants, allPatternsListParam, morphPosition, wordPosition)
                    g = nx.DiGraph()# хранится граф (networkx)
                    newNodeName = curPointWord.word.word_text + "_" + str(i)
                    g.add_node(newNodeName)
                    newParsePoint = ParsePoint(new_word_list, [], 0, 1, [], numberChildPoint, att, g)
                    numberChildPoint += 1
                    listNewParsePoints.append(newParsePoint)
            if listNewParsePoints != []:
                return (listNewParsePoints, [i])
        return None

    def checkWord(self, depWord, parseVariant,
                  gPattern):  # на вход - потенциальное зависимое слово(или потенциальный предлог), модель управления
        #  Удовлетворяет ли требованиям данный вариант разбора данного слова
        constr = gPattern.dependentWordConstraints
        morphForm = depWord.forms[parseVariant].morph
        normal = depWord.forms[parseVariant].normal_form
        if gPattern.level != 3 or (gPattern.level == 3 and gPattern.dependentWord == normal):
            return morphForm.check_imp(constr)
        return False

    def getNewParsePoint(self, maxNumberPoint):
        '''create new ParsePoint, child for self'''
        print("------")
        att_res = self.attempts.next()
        #print(ans)
        if att_res == None:
            return None
        (potMain, potPattern, potDep, potDepParseVariant) = att_res
        depWord = self.parsePointWordList[potDep].word
        usedDepMorph = depWord.forms[potDepParseVariant]
        newParsePoint = self.apply(potMain, potDep, usedDepMorph, potPattern, maxNumberPoint)
        self.childParsePoint.append(newParsePoint)
        return (newParsePoint, potPattern)



    def checkEndParse(self):
        '''check that all words in this ParsePoint are parsed'''
        # вроде достаточно проверять self.attempts.flagEnd
        for curPointWord in self.parsePointWordList:
            if (curPointWord.parsed == False):
                return False
        return True

    def checkPrep(self):
        for i in range(len(self.parsePointWordList)):
            curMain = self.parsePointWordList[i]
            if curMain.usedMorphAnswer.morph.s_cl == 'preposition':
                if not curMain.usedGp: # у предлога нет зависимого
                    return False
                if len(curMain.usedGp) > 1: # у предлога больше одного зависимого
                    return False
                curDep = curMain.usedGp[0].depWord
                if curDep.numberInSentence <= i: # у предлога зависимое должно стоять справа от главного
                    return False
        return True
