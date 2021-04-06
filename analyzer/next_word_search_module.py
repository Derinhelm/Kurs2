import copy

SIMILAR_PARAM = 450


def find_best_pattern_in_list(param_list):
    """find the best pair main word + pattern, return number of this pair"""
    # param_list - вида [(номер главного слова, модель управления)]
    best_pattern_1_number, best_pattern_2_number, best_pattern_3_number = None, None, None
    mark_best_pattern_1, mark_best_pattern_2, mark_best_pattern_3 = -1009090909090, -1090909090, -109090909090909
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


class DepWordSeacher:
    def __init__(self, dep_list, cur_main, len_sent):
        self.pos_variants_dict = {} # словарь, ключ - номер слова в предложении, значение - список номеров словоформ
        self.len_sent = len_sent #
        for (word_pos, variant_number) in dep_list:
            if word_pos in self.pos_variants_dict.keys():
                self.pos_variants_dict[word_pos].append(variant_number)
            else:
                self.pos_variants_dict[word_pos] = [variant_number]
        for word_pos in self.pos_variants_dict.keys():
            self.pos_variants_dict[word_pos].sort()
        self.left_word_pos = cur_main
        self.right_word_pos = cur_main
        self.main_pos = cur_main
        self.set_next_left()
        self.set_next_right()
        if self.right_word_pos is not None:
            self.right_word = True
            self.cur_word_pos = self.right_word_pos
        else:
            self.right_word = False
            self.cur_word_pos = self.left_word_pos
        self.flag_dep_end = False

    def next_dep(self):
        if self.flag_dep_end:
            return None
        ans_position = self.cur_word_pos
        ans_variant = self.pos_variants_dict[self.cur_word_pos].pop(0)
        # вернули самый вероятный вариант из еще непросмотренных
        if len(self.pos_variants_dict[self.cur_word_pos]) == 0:
            self.pos_variants_dict.pop(self.cur_word_pos)
            self.set_next_cur_word()
        return (ans_position, ans_variant)

    def set_next_cur_word(self):
        if self.right_word:
            #рассматривали слово справа
            self.set_next_right()
        else:
            #рассматривали слово слева
            self.set_next_left()
        if self.flag_dep_end: # self.left_word_pos = right_word_pos = None
            return
        if self.left_word_pos is None:
            self.cur_word_pos = self.right_word_pos
            self.right_word = True
        elif self.right_word_pos is None:
            self.cur_word_pos = self.left_word_pos
            self.right_word = False
        else:
            left_dist = self.main_pos - self.left_word_pos
            right_dist = self.right_word_pos - self.main_pos
            if left_dist > right_dist:
                self.cur_word_pos = self.right_word_pos
                self.right_word = True
            elif left_dist < right_dist:
                self.cur_word_pos = self.left_word_pos
                self.right_word = False
            else: # right_dist = left_dist
                if self.right_word:
                    self.cur_word_pos = self.left_word_pos
                    self.right_word = False
                else:
                    self.cur_word_pos = self.right_word_pos
                    self.right_word = True

    def set_next_right(self):
        if self.right_word_pos is None:
            return
        self.right_word_pos += 1
        while self.right_word_pos < self.len_sent and self.right_word_pos not in self.pos_variants_dict.keys():
            self.right_word_pos += 1

        if self.right_word_pos >= self.len_sent:
            self.right_word_pos = None
            if self.left_word_pos is None:
                self.flag_dep_end = True

    def set_next_left(self):
        if self.left_word_pos is None:
            return
        self.left_word_pos -= 1
        while self.left_word_pos >= 0 and self.left_word_pos not in self.pos_variants_dict.keys():
            self.left_word_pos -= 1

        if self.left_word_pos < 0:
            self.left_word_pos = None
            if self.right_word_pos is None:
                self.flag_dep_end = True

    def delete_word(self, number_word_pos):
        if number_word_pos in self.pos_variants_dict.keys():
            if self.cur_word_pos == number_word_pos:
                self.set_next_cur_word()
            else:
                if self.right_word_pos == number_word_pos:
                    self.set_next_right()
                elif self.left_word_pos == number_word_pos:
                    self.set_next_left()
            self.pos_variants_dict.pop(number_word_pos)
            if self.pos_variants_dict == {}:
                self.flag_dep_end = True

    def is_end(self):
        return self.flag_dep_end

class MorphInfo:
    def __init__(self, pp_words, sentence_info):
        # список вида [[модели управления]],
        # для каждого варианта разбора каждого слова храним его возможные модели управления
        # j элементе i элемента all_patterns_list - список моделей управления для j варианта разбора i слова
        # word - WordInSentence, надо перевызывать
        self.sentence_info = sentence_info
        self.all_patterns_list = [self.sentence_info.get_word(word).get_all_form_patterns() for word in
                                  pp_words]  # для дальнешего извлечения моделей

        self.morph_position_dict = {}
        # ключ - морф.характеристика, значение - set из пар (позиция слова, номер варианта разбора)

        self.word_position_dict = {}
        # ключ - нач.форма слова, значение - set из пар (позиция слова, номер варианта разбора)
        for word_position in range(len(pp_words)):
            word = self.sentence_info.get_word(pp_words[word_position])
            for form_position in range(len(word.forms)):
                form = word.forms[form_position]
                for cur_param in form.morph.get_imp():
                    if cur_param not in self.morph_position_dict.keys():
                        self.morph_position_dict[cur_param] = set()
                    self.morph_position_dict[cur_param].add((word_position, form_position))

                if form.normal_form not in self.word_position_dict.keys():
                    self.word_position_dict[form.normal_form] = set()
                self.word_position_dict[form.normal_form].add((word_position, form_position))

    def create_dep_forms_set(self, pattern):
        morph_constraints = pattern.get_dep_morph_constraints()
        word_constraints = pattern.get_dep_word()
        if not morph_constraints[0] in self.morph_position_dict.keys():
            return None
        itog_set = copy.deepcopy(set(self.morph_position_dict[morph_constraints[0]]))
        for i in range(1, len(morph_constraints)):
            if not morph_constraints[i] in self.morph_position_dict.keys():
                return None
            itog_set = itog_set.intersection(self.morph_position_dict[morph_constraints[i]])
        if word_constraints is not None:
            if word_constraints not in self.word_position_dict.keys():
                return None
            itog_set = itog_set.intersection(self.word_position_dict[word_constraints])
        return itog_set

    def get_patterns_for_form(self, word_pos, word_variant):
        return self.all_patterns_list[word_pos][word_variant]

class NextWordSearcher:
    def __init__(self, pp_words, sentence_info):


        self.word_variants_list = []  # список, в какой позиции, какой вариант мб
        # список неразобранных словоформ [(номер слова, номер варианта)]

        self.sentence_info = sentence_info
        self.word_variants_list = [(i, j) for i in range(len(pp_words)) for j in range(len(self.sentence_info.get_word(pp_words[i]).forms))]

        self.sentence_info = sentence_info
        self.morph_info = MorphInfo(pp_words, sentence_info)


        self.len_sent = len(pp_words)

        self.main_pattern_list = []
        # список вида [(главное слово, модель управления)]
        self.unavailable = set()
        self.current_main = None
        self.current_pattern = None
        self.current_dep_variant = None
        self.current_dep_position = None
        self.dep_creator = None
        self.dep_dict = {}  # по главному + модели возвращается DepWordSeacher
        self.flag_end = False

    def next(self):
        if self.dep_creator is not None:
            new_dep = self.dep_creator.next_dep()
            if new_dep is not None:
                (self.current_dep_position, self.current_dep_variant) = new_dep
                return
        self.next_main_pattern()
        if self.flag_end:
            return None
        return self.current_main, self.current_pattern, self.current_dep_position, self.current_dep_variant

    def find_potential_main_pattern(self):
        number_of_best_pair = find_best_pattern_in_list(self.main_pattern_list)
        if number_of_best_pair is None:
            return None, None
        (current_main, current_pattern) = self.main_pattern_list[number_of_best_pair]
        dep = self.get_dep_for_new_pair_main_pattern(current_main, current_pattern)
        return number_of_best_pair, dep

    def delete_similar(self):
        del_index = []
        for i in range(len(self.main_pattern_list)):
            (main, pat) = self.main_pattern_list[i]
            if self.current_main == main and self.current_pattern.is_identical_dif_level(pat):
                if self.current_pattern.level > pat.level: #todo объяснение
                    del_index.append(i)

            elif self.current_main == main and self.current_pattern.is_extended(pat):#todo объяснение
                # тк мы рассмотрели current_main раньше pat, то current_main.mark >= pat.mark
                del_index.append(i)

        for i in range(len(del_index) - 1, -1, -1):
            self.delete_main_pattern_pair_with_number(del_index[i])



    def next_main_pattern(self):
        """Используется только для получения новой пары главное+модель, старая себя исчерпала"""
        # ищем пару (главное слово, модель) с максимальной оценкой(лучше 3 уровня, потом 2, потом 1)
        if self.current_main is not None:
            # удаляем пару (главное, модель) из списка и из словаря,
            # тк мы проверили для нее все зависимые, больше с ней ничего сделать нельзя
            self.delete_main_pattern_pair((self.current_main, self.current_pattern))

        (number_of_best_pair, dep_creat) = self.find_potential_main_pattern()
        # может быть три исхода 1. нашли, все ок
        # 2. надо заново запустить next_main_pattern, тк для найденной пары (главное, модель) нет зависимых
        # 3. больше нет пар
        while (number_of_best_pair is not None) and (dep_creat is None):
            # для данной пары (главное, модель) нет зависимых
            self.delete_main_pattern_pair_with_number(number_of_best_pair)

            (number_of_best_pair, dep_creat) = self.find_potential_main_pattern()
        if number_of_best_pair is None:
            # больше списке пар self.main_pattern_list нет вариантов
            self.flag_end = True
            return None
        (self.current_main, self.current_pattern) = self.main_pattern_list[number_of_best_pair]
        # удаляем похожие (для данного слова для модели 3 уровня удаляем 2 и 1 уровня с такими же требованиями и тп)
        self.delete_similar()
        self.dep_creator = dep_creat
        self.current_dep_position, self.current_dep_variant = self.dep_creator.next_dep()
        return self.current_main, self.current_pattern

    def delete_variants_of_new_parsed(self, new_parsed):
        delete_indexes = []
        for i in range(len(self.word_variants_list)):
            (cur_position, cur_variant) = self.word_variants_list[i]
            if cur_position == new_parsed:
                self.unavailable.add((cur_position, cur_variant))
                delete_indexes.append(i)
        for i in range(len(delete_indexes) - 1, -1, -1):
            self.delete_main_pattern_pair_with_number(delete_indexes[i])

    def copy(self):
        # morphInfo - для всех NextWordSearcher общие
        # current_main, current_dep_position, current_dep_variant - числа, flag_end - Bool
        # current_pattern только указывает на константный класс GPatterns
        new_att = copy.copy(self)
        new_att.unavailable = copy.deepcopy(self.unavailable)
        new_att.dep_dict = {}
        # копирование ключей специально неглубокое, чтобы pattern в ключе остался таким же
        for (key, value) in self.dep_dict.items():
            new_att.dep_dict[key] = copy.deepcopy(value)
        new_att.word_variants_list = copy.deepcopy(self.word_variants_list) # можно неглубокое ?
        #копирование специально неглубокое, чтобы не менять константные элементы
        new_att.main_pattern_list = copy.copy(self.main_pattern_list)
        new_att.dep_creator = copy.deepcopy(self.dep_creator)
        return new_att

    def create_first(self, main_pos, main_var):
        """"""
        patterns_main_word = self.morph_info.get_patterns_for_form(main_pos, main_var)
        self.main_pattern_list = [(main_pos, pattern) for pattern in patterns_main_word]

        self.delete_variants_of_new_parsed(main_pos)
        # здесь пока не валидны current_main, current_pattern, тк мб этот NextWordSearcher никогда не будет вычислен
        self.current_main = None
        self.current_pattern = None
        self.dep_creator = None
        self.current_dep_variant = None
        self.current_dep_position = None
        self.flag_end = False


    def create_child(self):
        """создаем новую структуру, дочернюю данной(в ней применена текущая модель управления)"""
        # self.current_dep_position, self.current_dep_variant - фиксируем, переводим его в main,
        # удаляем из Dep все с данным зависимым"
        new_parsed = self.current_dep_position
        self.add_new_main_patterns(self.current_dep_position, self.current_dep_variant)
        deleted_keys = []
        for key in self.dep_dict.keys():
            self.dep_dict[key].delete_word(new_parsed)
            if self.dep_dict[key].is_end():
                #после удаления слова из потенц.зависимых в dep_creator для этой пары главное + модель закончились слова
                deleted_keys.append(key)
        for del_key in deleted_keys:
            self.delete_main_pattern_pair(del_key)

            # работа с dep_creator применяемой пары главное + модель
        self.delete_variants_of_new_parsed(new_parsed)
        self.dep_creator.delete_word(new_parsed)
        if not self.dep_creator.is_end():
            # для данной пары (главное, модель) еще могут быть зависимые(например, в случае однородности),
            # сохраняем информацию о зависимых
            self.dep_dict[(self.current_main, self.current_pattern)] = self.dep_creator
        self.dep_creator = None
        self.current_main = None
        self.current_pattern = None
        self.current_dep_position = None
        self.current_dep_variant = None

    def create_dep(self, pattern, main_index):
        itog_set = self.morph_info.create_dep_forms_set(pattern)
        if itog_set is None:
            return None
        itog_set = itog_set.difference(self.unavailable)
        if itog_set == set():
            return None
        dep_pos_vars_for_constraints = sorted(itog_set)
        return DepWordSeacher(dep_pos_vars_for_constraints, main_index, self.len_sent)

    def add_new_main_patterns(self, cur_main_pos, cur_variant):
        patterns_new_main = self.morph_info.get_patterns_for_form(cur_main_pos, cur_variant)
        main_patterns_new_main = [(cur_main_pos, pattern) for pattern in patterns_new_main]
        self.main_pattern_list += main_patterns_new_main

    def get_dep_for_new_pair_main_pattern(self, new_main, new_pattern):
        new_key = (new_main, new_pattern)
        if new_key in self.dep_dict.keys():
            return self.dep_dict[new_key]
        else:
            dep = self.create_dep(new_pattern, new_main)
            if dep is None or dep.is_end():
                return None # для новой модели нет зависимых
            else:
                return dep

    def delete_main_pattern_pair(self, pair):
        self.main_pattern_list.remove(pair)
        if pair in self.dep_dict.keys():
            self.dep_dict.pop(pair)

    def delete_main_pattern_pair_with_number(self, pair_number):
        pair = self.main_pattern_list.pop(pair_number)
        if pair in self.dep_dict.keys():
            self.dep_dict.pop(pair)