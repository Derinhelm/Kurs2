import sys

import networkx as nx
import psycopg2
import pymorphy2

from parse_point_module import Word, ParsePointWord, ParsePoint
from visualise import parse_tree_visualize, parse_point_visualize


class Sentence:
    def __init__(self, con, morph, str1):
        self.input_str = ""
        self.word_list = []
        self.root_p_p = None  # заполняется потом, с помощью get_root_parse_point
        self.first_parse_words_indices = []  # слова, первые для разбора, в простых предложениях
        self.best_parse_points = []  # хранится список точек разбора, упорядоченных по убыванию оценки
        self.graph = nx.DiGraph()  # хранится граф (networkx)
        self.max_number_parse_point = 0
        self.dict_parse_points = {}  # словарь соответствия названия точки разбора и точки разбора
        self.all_patterns_list = []
        # список вида [[модели управления]],
        # для каждого варианта разбора каждого слова храним его возможные модели управления
        # j элементе i элемента all_patterns_list - список моделей управления для j варианта разбора i слова
        self.morph_position = {}
        # ключ - морф.характеристика, значение - set из пар (позиция слова, номер варианта разбора)
        self.word_position = {}
        # ключ - нач.форма слова, значение - set из пар (позиция слова, номер варианта разбора)

        self.set_string(con, morph, str1)
        self.create_dicts()
        self.create_all_patterns_list()

    def __repr__(self):
        return self.input_str

    def set_string(self, con, morph, input_str1):
        self.input_str = input_str1
        # слово в предложении - все, отделенное пробелом, точкой, ? ! ...(смотрим только на первую .)
        #: ; " ' началом предложения, запятой, (   ) тире вообще не учитываем(оно отделено пробелами),
        # дефис только в словах очень-очень и тп,
        punctuation = [' ', '?', '!', ':', ';', '\'', '\"', ',', '(', ')']
        cur_word = ""
        number_word = 0
        for i in range(len(self.input_str)):
            cur_symbol = self.input_str[i]
            if (cur_symbol in punctuation) or (
                    cur_symbol == '.' and (i == len(self.input_str) - 1 or self.input_str[i + 1] not in punctuation)):
                # (cur_symbol == '.' ... - точка, но не сокращение
                if len(cur_word) != 0:
                    self.word_list.append(Word(con, morph, cur_word.lower(), number_word))
                    number_word += 1
                    cur_word = ""
            elif cur_symbol != '-' or (len(cur_word) != 0):  # - и непустое слово -  это дефис
                cur_word = cur_word + cur_symbol
        if len(cur_word) != 0:
            self.word_list.append(Word(con, morph, cur_word.lower(), number_word))

    def add_morph_position(self, cur_morph_form, position_info):
        for cur_param in cur_morph_form.get_imp():
            if cur_param not in self.morph_position.keys():
                self.morph_position[cur_param] = set()
            self.morph_position[cur_param].add(position_info)

    def add_word_position(self, cur_word, position_info):
        if cur_word not in self.word_position.keys():
            self.word_position[cur_word] = set()
        self.word_position[cur_word].add(position_info)

    def create_dicts(self):
        for word_position in range(len(self.word_list)):
            word = self.word_list[word_position]
            for form_position in range(len(word.forms)):
                form = word.forms[form_position]
                self.add_morph_position(form.morph, (word_position, form_position))
                self.add_word_position(form.normal_form, (word_position, form_position))

    def create_all_patterns_list(self):
        self.all_patterns_list = [word.get_all_form_patterns() for word in self.word_list]

    def get_g_patterns(self, con):
        for cur_word in self.word_list:
            list_patterns_for_variants = cur_word.get_g_patterns(con)
            self.all_patterns_list.append(list_patterns_for_variants)

    def create_all_word_variants_list(self):
        all_word_variants_list = []
        for i in range(len(self.word_list)):
            all_word_variants_list += [(i, j) for j in range(len(self.word_list[i].forms))]
        return all_word_variants_list

    def get_root_parse_point(self):
        self.root_p_p = ParsePoint([], [], 0.0, 0, [], 0, None, None)
        root_name = self.root_p_p.__repr__()
        self.graph.add_node(root_name)
        self.dict_parse_points[root_name] = self.root_p_p
        all_word_variants_list = self.create_all_word_variants_list()
        for word in self.word_list:
            cur_parse_point_word = ParsePointWord(word)
            self.root_p_p.parse_point_word_list.append(cur_parse_point_word)
        verb_res = self.root_p_p.find_first_word(lambda m: m.s_cl == 'verb', all_word_variants_list,
                                                 self.all_patterns_list,
                                                 self.morph_position, self.word_position)
        if verb_res is not None:
            (list_new_parse_points, first_words) = verb_res
        else:
            # в предложении нет глагола
            noun_res = \
                self.root_p_p.find_first_word(lambda m: m.s_cl == 'noun' and m.case_morph == 'nominative',
                                            all_word_variants_list, self.all_patterns_list,
                                            self.morph_position,
                                            self.word_position)
            if noun_res is not None:
                (list_new_parse_points, first_words) = noun_res
            else:
                prep_res = self.root_p_p.find_first_word(lambda m: m.s_cl == 'preposition', all_word_variants_list,
                                                         self.all_patterns_list, self.morph_position,
                                                         self.word_position)
                if prep_res is not None:
                    (list_new_parse_points, first_words) = prep_res
                else:
                    print("В предложении нет глагола, сущ в И.п, предлога")
                    sys.exit()
        self.root_p_p.child_parse_point = list_new_parse_points
        self.max_number_parse_point = len(
            list_new_parse_points)
        # есть корневая точка и len(list_new_parse_points) ее дочерних,
        self.first_parse_words_indices = first_words
        self.best_parse_points = list_new_parse_points
        for cur_child in list_new_parse_points:
            child_name = cur_child.__repr__()
            self.graph.add_node(child_name)
            self.graph.add_edge(root_name, child_name, n="")
            self.dict_parse_points[child_name] = cur_child

    def insert_new_parse_point(self, new_point):
        '''insert new ParsePoint into best_parse_points'''
        self.best_parse_points.insert(0, new_point)

    def get_best_parse_point(self):
        return self.best_parse_points[0]

    def sint_parse(self):
        if self.root_p_p is None:
            self.get_root_parse_point()

        while 1:
            best_parse_point = self.get_best_parse_point()
            res = best_parse_point.get_new_parse_point(self.max_number_parse_point)
            # print(res)
            if res is None:
                print("Не разобрано!")
                return best_parse_point
            else:
                (new_point, pattern) = res
                self.max_number_parse_point += 1
                new_point_name = new_point.__repr__()
                self.graph.add_node(new_point_name)
                self.graph.add_edge(best_parse_point.__repr__(), new_point.__repr__(), n=pattern.__repr__())
                self.dict_parse_points[new_point_name] = new_point
                if new_point.check_end_parse():
                    if new_point.check_prep():
                        print("------")
                        return new_point
                else:
                    self.insert_new_parse_point(new_point)


class WordResult:
    def __init__(self, p, mf, w, gps):
        self.parsed = p
        self.morf_form = mf
        self.word = w
        self.used_g_patterns = gps

    def __repr__(self):
        if self.parsed:
            return self.word + ":" + self.morf_form.__repr__()
        return "Не разобрано"


def parse(con, morph, str1, count=1, need_trace=False):
    s = Sentence(con, morph, str1)
    res = None
    for i in range(count):
        print("------------------------------------------------------", i)
        res = s.sint_parse()
        if need_trace:
            parse_tree_visualize(s.graph, s.dict_parse_points, s.__repr__())  # визуализация дерева построения
        parse_point_visualize(res, str1)
    ans = []
    for cur_word in res.parse_point_word_list:
        cur_result = WordResult(cur_word.parsed, cur_word.used_morph_answer, cur_word.word.word_text, cur_word.used_gp)
        ans.append(cur_result)
    return ans


def easy_parse(s, count=1):
    con = psycopg2.connect(dbname='gpatterns_3', user='postgres',
                           password='postgres', host='localhost')
    morph = pymorphy2.MorphAnalyzer()
    parse(con, morph, s, count, True)

# print(a1)
