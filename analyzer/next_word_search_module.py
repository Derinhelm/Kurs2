import copy
from patterns import GPattern

SIMILAR_PARAM = 450

def triple_comparison(first, second):
    '''Сравниваются тройки (главное слово, зависимое слово, модель управления). Ответ на вопрос first > second ?'''
    (first_main_pos, (first_dep_pos, _), first_gp), (second_main_pos, (second_dep_pos, _), second_gp) = first, second
    if first_gp > second_gp:
        return True
    elif first_gp < second_gp:
        return False
    else: # модели одинаковы по уровню и оценке (что не бывает)
        return abs(first_main_pos - first_dep_pos) >= abs(second_main_pos - second_dep_pos)

def find_best_pattern_in_list(param_list):
    """find the best pair main word + pattern, return number of this pair"""
    # param_list - вида [(номер главного слова, модель управления)]
    best_pattern_1_number, best_pattern_2_number, best_pattern_3_number = None, None, None
    mark_best_pattern_1, mark_best_pattern_2, mark_best_pattern_3 = -10000000000, -10000000000, -10000000000
    for i in range(len(param_list)):
        cur_pattern = param_list[i][1]
        cur_mark = cur_pattern.mark
        cur_level = cur_pattern.level
        if cur_level == 1:
            if cur_mark > mark_best_pattern_1:
                mark_best_pattern_1 = cur_mark
                best_pattern_1_number = i
        elif cur_level == 2:
            if cur_mark > mark_best_pattern_2:
                mark_best_pattern_2 = cur_mark
                best_pattern_2_number = i
        else:
            if cur_mark > mark_best_pattern_3:
                mark_best_pattern_3 = cur_mark
                best_pattern_3_number = i

    if mark_best_pattern_1 != -1:
        if mark_best_pattern_2 != -1:
            if mark_best_pattern_3 != -1:
                # 1+, 2+, 3+
                if mark_best_pattern_2 - mark_best_pattern_3 > SIMILAR_PARAM:
                    if mark_best_pattern_1 - mark_best_pattern_2 > SIMILAR_PARAM:
                        return best_pattern_1_number
                    else:
                        return best_pattern_2_number
                else:
                    if mark_best_pattern_1 - mark_best_pattern_3 > SIMILAR_PARAM:
                        return best_pattern_1_number
                    else:
                        return best_pattern_3_number
            else:
                # 1+, 2+, 3-
                if mark_best_pattern_1 - mark_best_pattern_2 > SIMILAR_PARAM:
                    return best_pattern_1_number
                else:
                    return best_pattern_2_number
        else:
            if mark_best_pattern_3 != -1:
                # 1+, 2-, 3+
                if mark_best_pattern_1 - mark_best_pattern_3 > SIMILAR_PARAM:
                    return best_pattern_1_number
                else:
                    return best_pattern_3_number
            else:
                # 1+, 2-, 3-
                return best_pattern_1_number
    else:
        if mark_best_pattern_2 != -1:
            if mark_best_pattern_3 != -1:
                # 1-, 2+, 3+
                if mark_best_pattern_2 - mark_best_pattern_3 > SIMILAR_PARAM:
                    return best_pattern_2_number
                else:
                    return best_pattern_3_number
            else:
                # 1-, 2+, 3-
                return best_pattern_2_number
        else:
            if mark_best_pattern_3 != -1:
                # 1-, 2-, 3+
                return best_pattern_3_number
            else:
                # 1-, 2-, 3-
                return None

    # if best_pattern_3_number != None:
    #    return best_pattern_3_number
    # elif best_pattern_2_number != None:
    # if mark_best_pattern_2 >
    #    return best_pattern_2_number
    # elif best_pattern_1_number != None:
    #    return best_pattern_1_number
    # else:
    #    return None


class NextWordSearcher:
    def __init__(self, sentence_info, triples, last_parsed_word_pos: int, last_parsed_word_var: int, unparsed_wordforms):
        self.sentence_info = sentence_info
        self.triples = triples
        self.last_parsed_word_pos = last_parsed_word_pos # последняя разобранная словоформа. Перед первым запуском NextWordSearcher тройки с ней надо удалить из triples
        self.last_parsed_word_var = last_parsed_word_var
        self.unparsed_wordforms = unparsed_wordforms
        self.first_use = True

    def next(self):
        if self.first_use:
            self.first_use = False
            self.prepare_last_parsed()
        if len(self.triples) == 0:
            return None
        best_triple_index = 0
        best_triple = self.triples[0]
        for i in range(len(self.triples)):
            if self.triples[i][2] > best_triple[2]:
                best_triple_index, best_triple = i, self.triples[i]
        (best_main_pos, (best_dep_pos, best_dep_var), best_gp) = self.triples[best_triple_index]
        self.triples.pop(best_triple_index)
        return best_main_pos, best_gp, best_dep_pos, best_dep_var

    def prepare_last_parsed(self):
        # удаляем тройки, где новое разобранное слово - зависимое
        self.triples = [(main_pos, (dep_pos, dep_var), pattern)
            for (main_pos, (dep_pos, dep_var), pattern) in self.triples if dep_pos != self.last_parsed_word_pos]

        self.unparsed_wordforms = [(word_pos, word_var) for (word_pos, word_var) in self.unparsed_wordforms if word_pos != self.last_parsed_word_pos]
        # создаем новые тройки с новым разобранным словом, как с главным
        self.triples += [(self.last_parsed_word_pos, (dep_pos, dep_var), g_p) for (dep_pos, dep_var) in self.unparsed_wordforms
            for g_p in self.sentence_info.get_word_by_pos(self.last_parsed_word_pos).get_forms()[self.last_parsed_word_var].get_patterns()
            if self.is_satisfied_to_gp(dep_pos, dep_var, g_p)]

    def is_satisfied_to_gp(self, dep_pos: int, dep_var: int, gpattern: GPattern):
        dep_word = self.sentence_info.get_word_by_pos(dep_pos)
        # TODO никак не учитываются схожие модели разных уровней
        if gpattern.get_level() == 3 and dep_word.get_text() != gpattern.get_dep_word():
            return False
        dep_word_morph_params = dep_word.get_forms()[dep_var].get_morph().get_all_params()
        for constraint in gpattern.get_dep_morph_constraints():
            if constraint not in dep_word_morph_params:
                return False
        return True