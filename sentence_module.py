import copy
import sys

import psycopg2
import pymorphy2

from parse_point_module import WordInSentence, ParsePoint
from visualize import ParsePointTreeView
from word_module import Word


class Sentence:
    def __init__(self, str1):
        self.input_str = ""
        self.best_parse_points = []  # хранится список точек разбора, упорядоченных по убыванию оценки
        self.max_number_parse_point = 0

        word_list = self.split_string(str1)
        parse_point_word_list = []
        for i in range(len(word_list)):
            word = word_list[i]
            cur_parse_point_word = WordInSentence(word, i)
            parse_point_word_list.append(cur_parse_point_word)
        self.root_p_p = ParsePoint(parse_point_word_list)
        self.view = ParsePointTreeView(self.input_str, self.root_p_p.view)
        self.create_first_parse_points()

    def __repr__(self):
        return self.input_str

    def split_string(self, input_str1):
        self.input_str = input_str1
        # слово в предложении - все, отделенное пробелом, точкой, ? ! ...(смотрим только на первую .)
        #: ; " ' началом предложения, запятой, (   ) тире вообще не учитываем(оно отделено пробелами),
        # дефис только в словах очень-очень и тп,
        punctuation = [' ', '?', '!', ':', ';', '\'', '\"', ',', '(', ')']
        cur_word = ""
        morph_analyzer = pymorphy2.MorphAnalyzer()
        con = psycopg2.connect(dbname='gpatterns_3', user='postgres',
                               password='postgres', host='localhost')
        word_list = []
        for i in range(len(self.input_str)):
            cur_symbol = self.input_str[i]
            if (cur_symbol in punctuation) or (
                    cur_symbol == '.' and (i == len(self.input_str) - 1 or self.input_str[i + 1] not in punctuation)):
                # (cur_symbol == '.' ... - точка, но не сокращение
                if len(cur_word) != 0:
                    word_list.append(Word(con, morph_analyzer, cur_word.lower()))
                    cur_word = ""
            elif cur_symbol != '-' or (len(cur_word) != 0):  # - и непустое слово -  это дефис
                cur_word = cur_word + cur_symbol
        if len(cur_word) != 0:
            word_list.append(Word(con, morph_analyzer, cur_word.lower()))
        con.close()
        return word_list

    def create_first_parse_points(self):

        verb_res = self.root_p_p.find_first_word(lambda m: m.s_cl == 'verb')
        if verb_res:
            list_new_parse_points = verb_res
        else:
            # в предложении нет глагола
            noun_res = \
                self.root_p_p.find_first_word(lambda m: m.s_cl == 'noun' and m.case_morph == 'nominative')
            if noun_res:
                list_new_parse_points = noun_res
            else:
                prep_res = self.root_p_p.find_first_word(lambda m: m.s_cl == 'preposition')
                if prep_res:
                    list_new_parse_points = prep_res
                else:
                    print("В предложении нет глагола, сущ в И.п, предлога")
                    sys.exit()
        self.root_p_p.child_parse_point = list_new_parse_points
        self.max_number_parse_point = len(list_new_parse_points)
        # есть корневая точка и len(list_new_parse_points) ее дочерних,
        self.best_parse_points = copy.deepcopy(list_new_parse_points)
        for cur_child in list_new_parse_points:
            self.view.add_edge(self.root_p_p.view, cur_child.view)

    def insert_new_parse_point(self, new_point):
        """insert new ParsePoint into best_parse_points"""
        self.best_parse_points.insert(0, new_point)

    def get_best_parse_point(self):
        return self.best_parse_points[0]

    def sint_parse(self):

        while True:
            best_parse_point = self.get_best_parse_point()
            res = best_parse_point.get_new_parse_point(self.max_number_parse_point)
            # print(res)
            if res is None:
                print("Не разобрано!")
                return best_parse_point
            else:
                (new_point, pattern) = res
                self.max_number_parse_point += 1
                self.view.add_edge(best_parse_point.view, new_point.view, pattern.__repr__())
                if new_point.check_end_parse():
                    if new_point.check_prep():
                        print("------")
                        return new_point
                else:
                    self.insert_new_parse_point(new_point)
