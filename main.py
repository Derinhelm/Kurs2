from Functions import *
import pymorphy2
from parse_point_module import WordForm, Word, Gp, ParsePointWord, ParsePoint
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import sys
from visualise import parse_tree_visualize, parse_point_visualize


class Sentence:
    def __init__(self, con, morph, str1):
        self.inputStr = ""
        self.wordList = []
        self.rootPP = None  # заполняется потом, с помощью getRootParsePoint
        self.firstParseWordsIndices = []  # слова, первые для разбора, в простых предложениях
        self.bestParsePoints = [] # хранится список точек разбора, упорядоченных по убыванию оценки
        self.graph = nx.DiGraph()# хранится граф (networkx)
        self.maxNumberParsePoint = 0
        self.dictParsePoints = {} # словарь соответствия названия точки разбора и точки разбора
        self.allPatternsList = []
        # список вида [[модели управления]], для каждого варианта разбора каждого слова храним его возможные модели управления
        # j элементе i элемента allPatternsList - список моделей управления для j варианта разбора i слова
        self.morphPosition = {} # ключ - морф.характеристика, значение - set из пар (позиция слова, номер варианта разбора)
        self.wordPosition = {} # ключ - нач.форма слова, значение - set из пар (позиция слова, номер варианта разбора)

        self.setString(con, morph, str1)
        self.create_dicts()
        self.create_all_patterns_list()

    def __repr__(self):
        return self.inputStr

    def setString(self, con, morph, inputStr1):
        self.inputStr = inputStr1
        # слово в предложении - все, отделенное пробелом, точкой, ? ! ...(смотрим только на первую .)
        #: ; " ' началом предложения, запятой, (   ) тире вообще не учитываем(оно отделено пробелами),
        # дефис только в словах очень-очень и тп,
        punctuation = [' ', '?', '!', ':', ';', '\'', '\"', ',', '(', ')']
        curWord = ""
        numberWord = 0
        for i in range(len(self.inputStr)):
            cur_symbol = self.inputStr[i]
            if (cur_symbol in punctuation) or \
                    (cur_symbol == '.' and \
                        (i == len(self.inputStr) - 1 or \
                        not self.inputStr[i + 1] in punctuation)):
                #(cur_symbol == '.' ... - точка, но не сокращение
                if (len(curWord) != 0):
                    self.wordList.append(Word(con, morph, curWord.lower(), numberWord))
                    numberWord += 1
                    curWord = ""
            elif (cur_symbol != '-' or (len(curWord) != 0)):  # - и непустое слово -  это дефис
                curWord = curWord + cur_symbol
        if (len(curWord) != 0):
            self.wordList.append(Word(con, morph, curWord.lower(), numberWord))

    def add_morph_position(self, cur_morph_form, position_info):
        for cur_param in cur_morph_form.get_imp():
            if not cur_param in self.morphPosition.keys():
                self.morphPosition[cur_param] = set()
            self.morphPosition[cur_param].add(position_info)

    def add_word_position(self, cur_word, position_info):
        if not cur_word in self.wordPosition.keys():
            self.wordPosition[cur_word] = set()
        self.wordPosition[cur_word].add(position_info)

    def create_dicts(self):
        for word_position in range(len(self.wordList)):
            word = self.wordList[word_position]
            for form_position in range(len(word.forms)):
                form = word.forms[form_position]
                self.add_morph_position(form.morph, (word_position, form_position))
                self.add_word_position(form.normal_form, (word_position, form_position))

    def create_all_patterns_list(self):
        self.allPatternsList = [word.get_all_form_patterns() for word in self.wordList]

    def getGPatterns(self, con):
        for curWord in self.wordList:
            listPatternsForVariants = curWord.getGPatterns(con)
            self.allPatternsList.append(listPatternsForVariants)

    def create_all_word_variants_list(self):
        all_word_variants_list = []
        for i in range(len(self.wordList)):
            all_word_variants_list += [(i, j) for j in range(len(self.wordList[i].forms))]
        return all_word_variants_list

    def getRootParsePoint(self):
        self.rootPP = ParsePoint([], [], 0.0, 0, [], 0, None, None)
        rootName = self.rootPP.__repr__()
        self.graph.add_node(rootName)
        self.dictParsePoints[rootName] = self.rootPP
        all_word_variants_list = self.create_all_word_variants_list()
        for word in self.wordList:
            curParsePointWord = ParsePointWord(word)
            self.rootPP.parsePointWordList.append(curParsePointWord)
        verbRes = self.rootPP.find_first_word(lambda m: m.s_cl == 'verb', all_word_variants_list, self.allPatternsList, self.morphPosition, self.wordPosition)
        if verbRes != None:
            (listNewParsePoints, firstWords) = verbRes
        else:
            # в предложении нет глагола
            nounRes = self.rootPP.find_first_word(lambda m: m.s_cl == 'noun' and m.case_morph == 'nominative', all_word_variants_list, self.allPatternsList, self.morphPosition, self.wordPosition)
            if nounRes != None:
                (listNewParsePoints, firstWords) = nounRes
            else:
                prepRes = self.rootPP.find_first_word(lambda m: m.s_cl == 'preposition', all_word_variants_list, self.allPatternsList, self.morphPosition, self.wordPosition)
                if prepRes != None:
                    (listNewParsePoints, firstWords) = prepRes
                else:
                    print("В предложении нет глагола, сущ в И.п, предлога")
                    sys.exit()
        self.rootPP.childParsePoint = listNewParsePoints
        self.maxNumberParsePoint = len(listNewParsePoints) # есть корневая точка и len(listNewParsePoints) ее дочерних,
        self.firstParseWordsIndices = firstWords
        self.bestParsePoints = listNewParsePoints
        for curChild in listNewParsePoints:
            childName = curChild.__repr__()
            self.graph.add_node(childName)
            self.graph.add_edge(rootName, childName, n = "")
            self.dictParsePoints[childName] = curChild

    def insertNewParsePoint(self, newPoint):
        '''insert new ParsePoint into bestParsePoints'''
        self.bestParsePoints.insert(0, newPoint)

    def getBestParsePoint(self):
        return self.bestParsePoints[0]

    def sintParse(self):
        if self.rootPP == None:
            self.getRootParsePoint()

        while (1):
            bestParsePoint = self.getBestParsePoint()
            res = bestParsePoint.getNewParsePoint(self.maxNumberParsePoint)
            #print(res)
            if res == None:
                print("Не разобрано!")
                return bestParsePoint
            else:
                (newPoint, pattern) = res
                self.maxNumberParsePoint += 1
                newPointName = newPoint.__repr__()
                self.graph.add_node(newPointName)
                self.graph.add_edge(bestParsePoint.__repr__(), newPoint.__repr__(), n = pattern.__repr__())
                self.dictParsePoints[newPointName] = newPoint
                if newPoint.checkEndParse():
                    if newPoint.checkPrep():
                        print("------")
                        return newPoint
                else:
                    self.insertNewParsePoint(newPoint)

class WordResult:
    def __init__(self, p, mf, w, gps):
        self.parsed = p
        self.morfForm = mf
        self.word = w
        self.usedGPatterns = gps

    def __repr__(self):
        if self.parsed:
            return self.word + ":" + self.morfForm.__repr__()
        return "Не разобрано"

def parse(con, morph, str1, count = 1, needTrace=False):
    s = Sentence(con, morph, str1)
    for i in range(count):
        print("------------------------------------------------------", i)
        res = s.sintParse()
        if (needTrace):
            parse_tree_visualize(s.graph, s.dictParsePoints, s.__repr__()) # визуализация дерева построения
        parse_point_visualize(res, str1)
    ans = []
    for curWord in res.parsePointWordList:
        curResult = WordResult(curWord.parsed, curWord.usedMorphAnswer, curWord.word.word_text, curWord.usedGp)
        ans.append(curResult)
    return ans

def easy_parse(s, count = 1):
    con = psycopg2.connect(dbname='gpatterns_3', user='postgres',
                           password='postgres', host='localhost')
    morph = pymorphy2.MorphAnalyzer()
    parse(con, morph, s, count, True)

# print(a1)