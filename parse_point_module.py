import copy

import networkx as nx
import pymorphy2

from attempts_module import Attempts
from const_types import Morph
from functions import get_patterns


class WordForm:
    def __init__(self, con, morph: Morph, normal_form):
        self.normal_form = normal_form
        self.morph: Morph = morph
        self.g_patterns = []  # список из Gpattern, в которых данная словоформа мб главной
        self.create_patterns(con)

    def __repr__(self):
        return self.normal_form + " " + self.morph.__repr__()

    def create_patterns(self, con):
        cursor = con.cursor()
        morph_constr = self.morph.get_imp()
        cur_first = get_patterns(cursor, 1, main_morph_params=morph_constr)
        cur_sec = get_patterns(cursor, 2, main_morph_params=morph_constr, main_word_param=self.normal_form)
        cur_third = get_patterns(cursor, 3, main_morph_params=morph_constr, main_word_param=self.normal_form)
        cursor.close()
        self.g_patterns += cur_third
        self.g_patterns += cur_sec
        self.g_patterns += cur_first
        return

    def get_patterns(self):
        return self.g_patterns


class Word:
    def __init__(self, con, morph_analyzer: pymorphy2.MorphAnalyzer, word_text, number=-1):
        self.word_text = word_text
        self.forms = []
        self.number_in_sentence = number
        self.morph_parse(con, morph_analyzer)

    # toDo number_in_sentence убрать

    def morph_parse(self, con, morph_analyzer: pymorphy2.MorphAnalyzer):
        if self.word_text[-1] == '.':
            p = morph_analyzer.parse(self.word_text[:-1])
            abbr = True
        else:
            p = morph_analyzer.parse(self.word_text)
            abbr = False
        for cur_parse in p:
            if (abbr and 'Abbr' in cur_parse.tag) or \
                    (not abbr and 'Abbr' not in cur_parse.tag):
                # чтобы предлогу "к" не приписывался вариант кандидат
                morph = Morph(cur_parse, self.word_text)
                cur_form = WordForm(con, morph, cur_parse.normal_form)
                self.forms.append(cur_form)
        return

    def get_all_form_patterns(self):
        return [form.g_patterns for form in self.forms]


class Gp:
    def __init__(self, mod, dw):
        self.model = mod
        self.dep_word = dw


class ParsePointWord:
    def __init__(self, word):
        self.word = word
        self.parsed = False
        self.used_morph_answer = None  # типа WordForm
        self.used_gp = []  # типа Gp


class ParsePoint:
    direct_for_is_applicable = 1

    def __init__(self, ppwl, cl, mark, cpw, par, num, att, g):
        self.parse_point_word_list = ppwl
        self.child_parse_point = cl
        self.mark_parse_point = mark
        self.count_parsed_words = cpw
        self.parsed = par
        self.number_point = num
        self.attempts = att
        self.graph = g  # хранится граф (networkx)

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

    def apply(self, main_pp_word, depending_pp_word, used_morph_answer, g_pattern_to_apply, max_number_point):
        """create and return new child ParsePoint"""
        new_word_list = copy.deepcopy(self.parse_point_word_list)
        new_word_list[depending_pp_word].parsed = True
        new_word_list[depending_pp_word].used_morph_answer = used_morph_answer
        new_gp = Gp(g_pattern_to_apply, self.parse_point_word_list[depending_pp_word].word)
        new_word_list[main_pp_word].used_gp.append(new_gp)
        new_mark = self.mark_parse_point + g_pattern_to_apply.mark
        new_parsed_list = copy.deepcopy(self.parsed)
        new_parsed_list.append((main_pp_word, depending_pp_word))
        new_number = max_number_point + 1
        new_attempts = copy.deepcopy(self.attempts)
        new_attempts.apply()
        new_graph = copy.deepcopy(self.graph)
        dep_word = self.parse_point_word_list[depending_pp_word].word.word_text + "_" + str(depending_pp_word)
        main_word = self.parse_point_word_list[main_pp_word].word.word_text + "_" + str(main_pp_word)
        new_graph.add_node(dep_word)
        new_graph.add_edge(main_word, dep_word)
        return ParsePoint(new_word_list, [], new_mark, self.count_parsed_words + 1, new_parsed_list, new_number,
                          new_attempts,
                          new_graph)

    def find_first_word(self, fun, list_numbers_variants, all_patterns_list_param, morph_position, word_position):
        number_child_point = self.number_point + 1
        for i in range(len(self.parse_point_word_list)):
            cur_point_word = self.parse_point_word_list[i]
            list_new_parse_points = []
            for j in range(len(cur_point_word.word.forms)):
                cur_morph = cur_point_word.word.forms[j].morph
                if fun(cur_morph):
                    new_word_list = copy.deepcopy(self.parse_point_word_list)
                    new_word_list[i].parsed = True
                    new_word_list[i].used_morph_answer = copy.deepcopy(cur_point_word.word.forms[j])
                    cur_list_number_variants = copy.deepcopy(list_numbers_variants)
                    patterns_cur_variant = new_word_list[i].word.forms[j].g_patterns
                    att = Attempts(i, patterns_cur_variant, cur_list_number_variants, all_patterns_list_param,
                                   morph_position,
                                   word_position)
                    g = nx.DiGraph()  # хранится граф (networkx)
                    new_node_name = cur_point_word.word.word_text + "_" + str(i)
                    g.add_node(new_node_name)
                    new_parse_point = ParsePoint(new_word_list, [], 0, 1, [], number_child_point, att, g)
                    number_child_point += 1
                    list_new_parse_points.append(new_parse_point)
            if list_new_parse_points:
                return list_new_parse_points, [i]
        return None

    def get_new_parse_point(self, max_number_point):
        """create new ParsePoint, child for self"""
        print("------")
        att_res = self.attempts.next()
        # print(ans)
        if att_res is None:
            return None
        (pot_main, pot_pattern, pot_dep, pot_dep_parse_variant) = att_res
        dep_word = self.parse_point_word_list[pot_dep].word
        used_dep_morph = dep_word.forms[pot_dep_parse_variant]
        new_parse_point = self.apply(pot_main, pot_dep, used_dep_morph, pot_pattern, max_number_point)
        self.child_parse_point.append(new_parse_point)
        return new_parse_point, pot_pattern

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
            if cur_main.used_morph_answer.morph.s_cl == 'preposition':
                if not cur_main.used_gp:  # у предлога нет зависимого
                    return False
                if len(cur_main.used_gp) > 1:  # у предлога больше одного зависимого
                    return False
                cur_dep = cur_main.used_gp[0].dep_word
                if cur_dep.number_in_sentence <= i:  # у предлога зависимое должно стоять справа от главного
                    return False
        return True
