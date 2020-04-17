import copy

from attempts_module import Attempts
from patterns import GPattern
from visualize import ParsePointView


class Gp:
    def __init__(self, mod, dw):
        self.model = mod
        self.dep_word = dw


class WordInSentence:
    def __init__(self, word, number):
        self.word = word
        self.parsed = False
        self.used_morph_answer = None  # номер варианта разбора для разобранных слов
        self.used_gp = []  # типа Gp
        self.number_in_sentence = number

    def __repr__(self):
        if self.parsed:
            return self.get_morph().__repr__()
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

    def is_preposition(self):
        m = self.get_morph()
        if m is None:
            return None
        return m.s_cl == 'preposition'

    def add_gp(self, pattern: GPattern, dep_word):
        # dep_word - WordInSentence
        new_gp = Gp(pattern, dep_word)
        self.used_gp.append(new_gp)


class ParsePoint:
    direct_for_is_applicable = 1

    def __init__(self, ppwl):
        self.parse_point_word_list = ppwl
        self.child_parse_point = []
        self.count_parsed_words = 0
        self.parsed = []
        self.number_point = 0

        # список вида [[модели управления]],
        # для каждого варианта разбора каждого слова храним его возможные модели управления
        # j элементе i элемента all_patterns_list - список моделей управления для j варианта разбора i слова
        # word - WordInSentence, надо перевызывать
        all_patterns_list = [word.word.get_all_form_patterns() for word in self.parse_point_word_list]

        word_variants_list = []  # список, в какой позиции, какой вариант мб
        for i in range(len(self.parse_point_word_list)):
            word_variants_list += [(i, j) for j in range(len(self.parse_point_word_list[i].word.forms))]

        morph_position_dict = {}
        # ключ - морф.характеристика, значение - set из пар (позиция слова, номер варианта разбора)

        word_position_dict = {}
        # ключ - нач.форма слова, значение - set из пар (позиция слова, номер варианта разбора)
        for word_position in range(len(self.parse_point_word_list)):
            word = self.parse_point_word_list[word_position].word
            for form_position in range(len(word.forms)):
                form = word.forms[form_position]
                for cur_param in form.morph.get_imp():
                    if cur_param not in morph_position_dict.keys():
                        morph_position_dict[cur_param] = set()
                    morph_position_dict[cur_param].add((word_position, form_position))

                if form.normal_form not in word_position_dict.keys():
                    word_position_dict[form.normal_form] = set()
                word_position_dict[form.normal_form].add((word_position, form_position))

        self.attempts = Attempts(word_variants_list, all_patterns_list,
                                 morph_position_dict, word_position_dict)
        self.view = ParsePointView('root', "Точка " + str(self.number_point), len(self.parse_point_word_list))

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

        main_word = new_parse_point.parse_point_word_list[main_pos]
        new_parse_point.view = self.view.create_child_view(new_parse_point.__repr__(), main_word)
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

    # вызывается в Sentence
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

        dep_word = new_parse_point.parse_point_word_list[depending_pp_word_pos]
        main_word = new_parse_point.parse_point_word_list[main_pp_word_pos]
        new_parse_point.view = self.view.create_child_view(new_parse_point.__repr__(), main_word, dep_word)
        self.child_parse_point.append(new_parse_point)
        return new_parse_point, g_pattern_to_apply

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
