import copy
import sys

from attempts_module import Attempts
from patterns import GPattern
from visualize import ParsePointView, ParsePointTreeView
import psycopg2
import pymorphy2
from word_module import Word

class Gp:
    def __init__(self, mod, dw):
        self.model = mod
        self.dep_word = dw


class WordInSentence:
    def __init__(self, con, morph_analyzer: pymorphy2.MorphAnalyzer, word_text: str, number):
        self.word = Word(con, morph_analyzer, word_text)
        self.parsed = False
        self.used_morph_answer = None  # номер варианта разбора для разобранных слов
        self.used_gp = []  # типа Gp
        self.number_in_sentence = number

    def __repr__(self):
        if self.parsed:
            return self.word.word_text + ": " + self.get_morph().__repr__()
        return "not_parsed"

    def fix_morph_variant(self, variant_position: int):
        """слово становится разобранным"""
        self.parsed = True
        self.used_morph_answer = variant_position

    def get_form(self):
        if self.parsed:
            return self.word.forms[self.used_morph_answer]
        return None

    def get_morph(self):
        if self.parsed:
            return self.word.forms[self.used_morph_answer].morph
        return None

    def get_normal(self):
        if self.parsed:
            return self.word.forms[self.used_morph_answer].normal_form
        return None

    def get_word_text(self):
        return self.word.word_text

    def is_preposition(self):
        m = self.get_morph()
        if m is None:
            return False
        return m.is_preposition()

    def is_verb(self):
        m = self.get_morph()
        if m is None:
            return False
        return m.is_verb()

    def is_nominative(self):
        m = self.get_morph()
        if m is None:
            return False
        return m.is_nominative()

    def is_noun_or_adj(self):
        m = self.get_morph()
        if m is None:
            return False
        return m.is_noun_or_adj()

    def add_gp(self, pattern: GPattern, dep_word):
        # dep_word - WordInSentence
        new_gp = Gp(pattern, dep_word)
        self.used_gp.append(new_gp)


class ParsePoint:
    direct_for_is_applicable = 1

    def __init__(self, word_list, con, morph_analyzer, sent_title):
        self.parse_point_word_list = []
        for number in range(len(word_list)):
            word_text = word_list[number]
            cur_parse_point_word = WordInSentence(con, morph_analyzer, word_text, number)
            self.parse_point_word_list.append(cur_parse_point_word)

        self.child_parse_point = []
        self.count_parsed_words = 0
        self.parsed = []
        self.number_point = 0
        self.status = 'intermediate'


        self.attempts = Attempts(self.parse_point_word_list)
        self.view = ParsePointView('root', sent_title, len(self.parse_point_word_list))

    def __repr__(self):
        ans = str(self.number_point) + ":"
        for i in self.parsed:
            ans += str(i[0]) + "+" + str(i[1]) + ";"
        return ans

    def index(self, word1):
        # ищет в списке слов в данной точке разбора индекс данного слова(класса Word), вспомогательная функция
        for i in range(len(self.parse_point_word_list)):
            if self.parse_point_word_list[i].word == word1:
                return i
        return None

    @staticmethod
    def check_inderect_dependency(self, number_main, number_dep):
        # dep_word = self.parse_point_word_list[number_dep]
        # main_word = self.parse_point_word_list[number_main]
        return True  # toDo ПЕРЕПИСАТЬ!!!!

    @staticmethod
    def check_is_word_in_dependent_group(self, number_main, number_dep):
        return True  # toDo ПЕРЕПИСАТЬ!!!!!

    def create_status(self):
        if self.check_end_parse():
            if self.check_prep() and not self.verb_has_homogeneous_subject():
                self.status = 'right'
            else:
                self.status = 'wrong'
        else:
            self.status = 'intermediate'

    def close(self):
        self.status = 'intermediate-close'

    def copy(self):
        """create copy of ParsePoint"""
        # надо писать вручную из-за attempts.copy
        # count_parsed_words, number_point - числа
        new_parse_point = copy.copy(self)
        new_parse_point.parse_point_word_list = copy.deepcopy(
            self.parse_point_word_list)
        new_parse_point.child_parse_point = copy.deepcopy(
            self.child_parse_point)
        new_parse_point.parsed = copy.deepcopy(self.parsed)
        new_parse_point.attempts = self.attempts.copy()
        new_parse_point.view = copy.deepcopy(self.view)
        return new_parse_point

    def create_firsts_pp(self, main_pos, main_var, max_number_point):
        new_parse_point = self.copy()
        new_parse_point.parse_point_word_list[main_pos].fix_morph_variant(main_var)

        new_parse_point.child_parse_point = []
        new_parse_point.count_parsed_words += 1
        new_parse_point.number_point = max_number_point + 1
        new_parse_point.attempts.create_first(main_pos, main_var)
        new_parse_point.create_status()
        main_word = new_parse_point.parse_point_word_list[main_pos]
        new_parse_point.view = self.view.create_child_view(new_parse_point,  main_word)
        return new_parse_point

    def find_first_word(self, fun):
        max_number_point = self.number_point
        list_new_parse_points = []
        for word_position in range(len(self.parse_point_word_list)):
            cur_point_word = self.parse_point_word_list[word_position]
            for variant_number in range(len(cur_point_word.word.forms)):
                cur_morph = cur_point_word.word.forms[variant_number].morph
                if fun(cur_morph):
                    new_parse_point = self.create_firsts_pp(word_position, variant_number, max_number_point)
                    max_number_point += 1
                    list_new_parse_points.append(new_parse_point)
        return list_new_parse_points

    def create_child_parse_point(self, max_number_point):
        """create and return new child ParsePoint"""
        print("------")
        att_res = self.attempts.next()
        if att_res is None:
            return None
        (main_pp_word_pos, g_pattern_to_apply, depending_pp_word_pos, dep_variant) = att_res

        new_parse_point = self.copy()

        new_parse_point.parse_point_word_list[depending_pp_word_pos].fix_morph_variant(dep_variant)
        new_parse_point.parse_point_word_list[main_pp_word_pos].add_gp(g_pattern_to_apply,
                                        new_parse_point.parse_point_word_list[depending_pp_word_pos])

        new_parse_point.child_parse_point = []
        new_parse_point.count_parsed_words += 1
        new_parse_point.parsed.append((main_pp_word_pos, depending_pp_word_pos))

        new_parse_point.number_point = max_number_point + 1
        new_parse_point.attempts.create_child()
        new_parse_point.create_status()

        dep_word = new_parse_point.parse_point_word_list[depending_pp_word_pos]
        main_word = new_parse_point.parse_point_word_list[main_pp_word_pos]
        new_parse_point.view = self.view.create_child_view(new_parse_point, main_word, dep_word)
        self.child_parse_point.append(new_parse_point)
        word_pair_text = str(g_pattern_to_apply.get_mark()) + ": " + str(main_pp_word_pos) + " + " + str(depending_pp_word_pos)
        return new_parse_point, g_pattern_to_apply, word_pair_text

    def check_end_parse(self):
        """check that all words in this ParsePoint are parsed"""
        # вроде достаточно проверять self.attempts.flag_end
        for cur_point_word in self.parse_point_word_list:
            if not cur_point_word.parsed:
                return False
        return True

    def check_prep(self):
        for i in range(len(self.parse_point_word_list)):
            cur_main = self.parse_point_word_list[i]
            if cur_main.is_preposition():
                if not cur_main.used_gp:  # у предлога нет зависимого
                    return False
                if len(cur_main.used_gp) > 1:  # у предлога больше одного зависимого
                    return False
                cur_dep = cur_main.used_gp[0].dep_word
                if cur_dep.number_in_sentence <= i:  # у предлога зависимое должно стоять справа от главного
                    return False
        return True

    def verb_has_homogeneous_subject(self):
        #если у глагола есть два зависимых именной части речи (сущ, прил и тп) И.п, то это однородн.подлежащие
        for i in range(len(self.parse_point_word_list)):
            cur_main = self.parse_point_word_list[i]
            count_subject = 0
            if cur_main.is_verb():
                for cur_gp in cur_main.used_gp:
                    if cur_gp.dep_word.is_noun_or_adj():
                        if cur_gp.dep_word.is_nominative():
                            count_subject += 1
                            if count_subject > 1:
                                return True
        return False



class Sentence:
    def __init__(self, input_str):
        self.best_parse_points = []  # хранится список точек разбора, упорядоченных по убыванию оценки
        self.max_number_parse_point = 0

        word_list, sent_title = self.split_string(input_str)
        self.sent_title_numb = sent_title
        self.sent_title_without_numb = input_str
        con = psycopg2.connect(dbname='gpatterns_copy', user='postgres',
                               password='postgres', host='localhost')
        morph_analyzer = pymorphy2.MorphAnalyzer()
        self.root_p_p = ParsePoint(word_list, con, morph_analyzer, self.sent_title_without_numb)
        self.view = ParsePointTreeView(self.sent_title_numb, self.root_p_p.view)
        self.create_first_parse_points()
        con.close()

    def __repr__(self):
        return self.sent_title

    def split_string(self, input_str):
        # слово в предложении - все, отделенное пробелом, точкой, ? ! ...(смотрим только на первую .)
        #: ; " ' началом предложения, запятой, (   ) тире вообще не учитываем(оно отделено пробелами),
        # дефис только в словах очень-очень и тп,
        punctuation = [' ', '?', '!', ':', ';', '\'', '\"', ',', '(', ')']
        cur_word = ""
        word_list = []
        for i in range(len(input_str)):
            cur_symbol = input_str[i]
            if (cur_symbol in punctuation) or (
                    cur_symbol == '.' and (i == len(input_str) - 1 or input_str[i + 1] not in punctuation)):
                # (cur_symbol == '.' ... - точка, но не сокращение
                if len(cur_word) != 0:
                    word_list.append(cur_word.lower())
                    cur_word = ""
            elif cur_symbol != '-' or (len(cur_word) != 0):  # - и непустое слово -  это дефис
                cur_word = cur_word + cur_symbol
        if len(cur_word) != 0:
            word_list.append(cur_word.lower())

        s = ""
        for i in range(len(word_list)):
            s += word_list[i] + "_" + str(i) + " "
        return word_list, s[:-1] + input_str[-1]

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
        if len(self.best_parse_points) == 0:
            return None
        return self.best_parse_points[0]

    def close_point(self):
        self.best_parse_points[0].close()
        self.best_parse_points.pop(0)


    def sint_parse(self):

        while True:
            best_parse_point = self.get_best_parse_point()
            if best_parse_point is None:
                print("Не разобрано!")
                return None
            res = best_parse_point.create_child_parse_point(self.max_number_parse_point)
            print(res)
            if res is None:
                self.close_point()
                self.view.close_node(best_parse_point.view.point_label)
            else:
                (new_point, pattern, word_pair_text) = res
                self.max_number_parse_point += 1
                self.view.add_edge(best_parse_point.view, new_point.view, pattern, word_pair_text)
                if new_point.status == 'right':
                        print("------")
                        return new_point
                else:
                    self.insert_new_parse_point(new_point)
