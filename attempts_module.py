import copy

SIMILAR_PARAM = 450


def find_best_pattern_in_list(param_list):
    '''find the best pair main word + pattern, return number of this pair'''
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


# noinspection PySimplifyBooleanCheck
class dep_words:
    def __init__(self, dep, cur_main):
        self.left_dep_words = copy.deepcopy(dep)
        self.left_dep_words = list(filter(lambda x: x[0] < cur_main, self.left_dep_words))
        self.right_dep_words = copy.deepcopy(dep)
        self.right_dep_words = list(filter(lambda x: x[0] > cur_main, self.right_dep_words))
        self.dep_direction = 1  # 1 - вправо, -1 - влево
        self.dep_words = self.right_dep_words  # потом будет left_dep_words
        self.flag_other_direction = False
        self.point_cur_dep = 0
        self.flag_end = False
        if self.dep_words != []:
            self.cur_dep = self.dep_words[self.point_cur_dep]
        else:
            self.cur_dep = None
            self.change_direct()

    def next(self):
        self.point_cur_dep += 1
        if self.point_cur_dep != len(self.dep_words):
            self.cur_dep = self.dep_words[self.point_cur_dep]
            return self.dep_words[self.point_cur_dep]
        return self.change_direct()

    def change_dep_list(self, new_dep):
        if self.dep_direction == 1:
            self.right_dep_words = new_dep
            self.dep_words = self.right_dep_words
        else:
            self.left_dep_words = new_dep
            self.dep_words = self.left_dep_words

    def delete_number_from_dep_list(self, delete_dep_number):
        new_dep = list(filter(lambda x: x[0] != delete_dep_number, self.dep_words))
        self.change_dep_list(new_dep)

    def delete_in_cur_half(self, delete_dep_number):
        # меняем dep_words, тк найденное зависимое слово было в dep_words, а не в другом направлении
        while self.point_cur_dep != len(self.dep_words) and self.dep_words[self.point_cur_dep][0] == delete_dep_number:
            self.point_cur_dep += 1
        if self.point_cur_dep == len(self.dep_words):
            self.delete_number_from_dep_list(delete_dep_number)
            return None
        old_len = len(self.dep_words)
        self.delete_number_from_dep_list(delete_dep_number)
        count_del = old_len - len(self.dep_words)
        self.point_cur_dep -= count_del
        self.cur_dep = self.dep_words[self.point_cur_dep]
        return self.cur_dep

        # указатель текущего зависимого надо поставить на следующее в dep_words значение
        # , у которого первое поле != удаляемому

    # варианты 1. delete_dep_number = 2 [(1, 0), (1, 1), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1)],
    # результат [(1, 0), (1, 1), (3, 0), (3, 1)] cur_dep = (3, 0)
    # 2. delete_dep_number = 2 [(1, 0), (1, 1), (2, 0), (2, 1), (2, 2)],
    # результат [(1, 0), (1, 1)], и надо менять направление
    # если нельзя поменять направление, то переходим к следующей модели(или к следующему главному)

    def delete_from_two_part(self, delete_dep_number):
        left_part = list(filter(lambda x: x[0] == delete_dep_number, self.left_dep_words))
        # noinspection PySimplifyBooleanCheck
        if left_part != []:
            # удаляемое в левой половине
            if self.dep_direction == -1:
                # левая часть - текущая
                self.delete_in_cur_half(delete_dep_number)
            else:
                self.left_dep_words = list(filter(lambda x: x[0] != delete_dep_number, self.left_dep_words))
                return self.left_dep_words
        else:
            # удаляемое в правой половине
            if self.dep_direction == 1:
                # правая - текущая
                self.delete_in_cur_half(delete_dep_number)
            else:
                self.right_dep_words = list(filter(lambda x: x[0] != delete_dep_number, self.right_dep_words))
                return self.right_dep_words

    def change_direct(self):
        if not self.flag_other_direction:
            # Смотрели только в одном направлении, смотрим в другом
            self.flag_other_direction = True
            self.point_cur_dep = 0
            self.dep_words = self.left_dep_words
            self.dep_direction *= -1
            if len(self.dep_words) > 0:
                self.cur_dep = self.dep_words[self.point_cur_dep]
                return self.dep_words[0]
        self.flag_end = True
        return None


# noinspection PyComparisonWithNone
class Attempts:
    def __init__(self, main_word_index, pattterns_main_word, dep, all_patterns_list_param, morph_position,
                 word_position):
        self.all_patterns_list = all_patterns_list_param  # для дальнешего извлечения моделей
        self.main_pattern_list = [(main_word_index, pattern) for pattern in pattterns_main_word]
        # список вида [(главное слово, модель управления)]
        self.dependents_list = dep
        self.unavailable = set()
        self.delete_variants_of_new_parsed(main_word_index)
        self.current_main = None
        self.current_pattern = None
        self.current_dep = None
        self.current_main_pattern_index = None  # индекс текущей пары главное + модель в main_pattern_list
        self.dep_dict = {}  # по главному + модели возвращается dep_words
        self.flag_end = False
        self.morph_position = morph_position
        self.word_position = word_position

    # noinspection PyComparisonWithNone
    def next(self):
        if self.current_dep is not None:
            new_dep = self.current_dep.next()
            if new_dep is not None:
                return
        self.next_main_pattern()
        if self.flag_end:
            return None
        return self.current_main, self.current_pattern, self.current_dep.cur_dep[0], self.current_dep.cur_dep[1]

    def find_potential_main_pattern(self):
        # может быть три исхода 1. нашли, все ок
        # 2. надо заново запустить next_main_pattern, тк для найденной пары (главное, модель) нет зависимых
        # 3. больше нет пар

        number_of_best_pair = find_best_pattern_in_list(self.main_pattern_list)
        if number_of_best_pair is None:
            return None, None
        (current_main, current_pattern) = self.main_pattern_list[number_of_best_pair]
        current_dep = self.get_dep_for_new_pair_main_pattern(current_main, current_pattern)
        return number_of_best_pair, current_dep

    # noinspection PyComparisonWithNone
    def next_main_pattern(self):
        '''Используется только для получения новой пары главное+модель, старая себя исчерпала'''
        # ищем пару (главное слово, модель) с максимальной оценкой(лучше 3 уровня, потом 2, потом 1)
        if self.current_main_pattern_index is not None:
            # удаляем пару (главное, модель) из списка и из словаря,
            # тк мы проверили для нее все зависимые, больше с ней ничего сделать нельзя
            self.main_pattern_list.pop(self.current_main_pattern_index)
        if (self.current_main, self.current_pattern) in self.dep_dict.keys():
            self.dep_dict.pop((self.current_main, self.current_pattern))
        (number_of_best_pair, current_dep) = self.find_potential_main_pattern()
        while (number_of_best_pair is not None) and (current_dep is None):
            # для данной пары (главное, модель) нет зависимых
            self.main_pattern_list.pop(number_of_best_pair)
            (number_of_best_pair, current_dep) = self.find_potential_main_pattern()
        print(current_dep)
        if number_of_best_pair is None:
            # больше списке пар self.main_pattern_list нет вариантов
            self.flag_end = True
            return None
        self.current_main_pattern_index = number_of_best_pair
        (self.current_main, self.current_pattern) = self.main_pattern_list[number_of_best_pair]
        self.current_dep = current_dep
        return self.current_main, self.current_pattern

    def delete_variants_of_new_parsed(self, new_parsed):
        new_dependents_list = []
        for (cur_position, cur_variant) in self.dependents_list:
            if cur_position == new_parsed:
                self.unavailable.add((cur_position, cur_variant))
            else:
                new_dependents_list.append((cur_position, cur_variant))
        self.dependents_list = new_dependents_list

    def apply(self):
        '''current_dep - фиксируем, переводим его в main, удаляем из Dep все с данным зависимым'''
        new_parsed = self.current_dep.cur_dep[0]
        self.add_new_main_patterns(self.current_dep.cur_dep)
        deleted_keys = []
        for key in self.dep_dict.keys():
            del_res = self.dep_dict[key].delete_from_two_part(new_parsed)
            # None возвращается, если запустили delete_in_cur_half, и она вернула None(те пот.зависимые закончились)
            # те для данной пары key = (главное, модель) в новой точке разбора нет зависимых,
            # те ее надо удалить из словаря и из списка
            if del_res is None:
                deleted_keys.append(key)
                self.main_pattern_list.remove(key)
        for del_key in deleted_keys:
            self.dep_dict.pop(del_key)
        self.delete_variants_of_new_parsed(new_parsed)
        del_res = self.current_dep.delete_in_cur_half(new_parsed)
        if del_res is not None:
            # для данной пары (главное, модель) еще могут быть зависимые(например, в случае однородности),
            # сохраняем информацию о зависимых
            self.dep_dict[(self.current_main, self.current_pattern)] = self.current_dep
        self.current_dep = None

    # noinspection PyComparisonWithNone
    def create_dep(self, pattern, main_index):
        morph_constraints = pattern.get_dep_morph_constraints()
        word_constraints = pattern.get_dep_word()
        if not morph_constraints[0] in self.morph_position.keys():
            return None
        itog_set = copy.deepcopy(set(self.morph_position[morph_constraints[0]]))
        for i in range(1, len(morph_constraints)):
            if not morph_constraints[i] in self.morph_position.keys():
                return None
            itog_set = itog_set.intersection(self.morph_position[morph_constraints[i]])
        if word_constraints is not None:
            if word_constraints not in self.word_position.keys():
                return None
            itog_set = itog_set.intersection(self.word_position[word_constraints])
        itog_set = itog_set.difference(self.unavailable)
        if itog_set == set():
            return None
        dep_pos_vars_for_constraints = sorted(itog_set)
        return dep_words(dep_pos_vars_for_constraints, main_index)

    def add_new_main_patterns(self, new_main):
        cur_main = new_main[0]
        cur_variant = new_main[1]
        patterns_new_main = self.all_patterns_list[cur_main][cur_variant]

        main_patterns_new_main = [(cur_main, pattern) for pattern in patterns_new_main]
        self.main_pattern_list += main_patterns_new_main

    def get_dep_for_new_pair_main_pattern(self, new_main, new_pattern):
        new_key = (new_main, new_pattern)
        if new_key in self.dep_dict.keys():
            return self.dep_dict[new_key]
        else:
            current_dep = self.create_dep(new_pattern, new_main)
            if current_dep is not None:
                return current_dep
            else:
                return None  # для новой модели нет зависимых, идем к следующей
