import copy
import sys
from timeit import default_timer as timer
from itertools import groupby

import networkx as nx
import psycopg2
import pymorphy2
import re

from next_word_search_module import NextWordSearcher
from analyzer.patterns import GPattern
from visualize import ParsePointView, ParsePointTreeView
from word_module import Word

MAX_PARSING_TIME = 60

class WordInSentence:
    def __init__(self, number_in_sentence: int):
        self.parsed = False
        self.used_morph_answer = None  # номер варианта разбора для разобранных слов
        self.number_in_sentence = number_in_sentence

    def __repr__(self):
        if self.parsed:
            return "word № " + str(self.number_in_sentence) + ", variant " + str(self.used_morph_answer)
        return "word № " + str(self.number_in_sentence) + " not_parsed"

    def __eq__(self, other):
        '''Провеяется, что выбраны одинаковые варианты разбора словоформы'''
        if self.number_in_sentence != other.number_in_sentence:
            return False

        if self.parsed != other.parsed:
            return False

        if self.used_morph_answer != other.used_morph_answer:
            return False

        return True

    def get_number(self):
        return self.number_in_sentence

    def __hash__(self):
        return hash(self.number_in_sentence) # TODO: нормально ли?

    def fix_morph_variant(self, variant_position: int):
        """слово становится разобранным"""
        self.parsed = True
        self.used_morph_answer = variant_position

    def is_parsed(self):
        return self.parsed

class Gp:
    def __init__(self, mod: GPattern, dw: WordInSentence):
        self.model = mod
        self.dep_word = dw

    def get_dep_word(self):
        return self.dep_word

    def get_pattern(self):
        return self.model

    def __repr__(self):
        return str(self.dep_word.get_number())

class SentenceInfo:
    '''Хранит информацию о вариантах разбора каждого слова из предложения.'''
    def __init__(self, input_str: str):
        word_texts, self.sent_title_with_numbers, self.punctuation_indexes = self.split_string(input_str)
        self.sent_title_without_numb = input_str
        con = psycopg2.connect(dbname='gpatterns', user='postgres',
                               password='postgres', host='localhost', port='5432')
        morph_analyzer = pymorphy2.MorphAnalyzer()
        self.words = []  # [Word]
        for word_text in word_texts:
            print("Начата обработка слова ", word_text)
            word_info = Word(morph_analyzer, word_text)
            self.words.append(word_info)
            print("Закончена обработка слова", word_text)

        lexemes = set()
        for w in self.words:
            lexemes |= set(w.get_all_lexema_variants()) # Собираем все варианты начальных форм слов в предложении

        for w in self.words:
            w.create_patterns(con, lexemes)
        con.close()

    def __repr__(self):
        return self.sent_title_without_numb

    def get_form_info(self, word: WordInSentence):
        if word.parsed:
            return self.words[word.number_in_sentence].get_variant(word.used_morph_answer)
        return None

    def get_text(self, word: WordInSentence):
        return self.words[word.number_in_sentence].get_text()

    def get_word(self, word: WordInSentence):
        return self.words[word.number_in_sentence]

    def get_word_by_pos(self, word_pos):
        return self.words[word_pos]

    def get_count_of_words(self):
        return len(self.words)

    def get_word_texts(self) -> [str]:
        '''возвращает список слов из предложения'''
        return [w.get_text() for w in self.words]

    def get_words(self):
        return self.words

    def get_sent_title_with_numbers(self):
        return self.sent_title_with_numbers

    def get_word_parsing_variant(self, word: WordInSentence):
        return self.get_form_info(word)

    def split_string(self, input_str):
        # слово в предложении - все, отделенное пробелом, точкой, ? ! ...(смотрим только на первую .)
        #: ; " ' началом предложения, запятой, (   ) тире вообще не учитываем(оно отделено пробелами),
        # дефис только в словах очень-очень и тп,
        punctuation = [' ', '?', '!', ':', ';', '\'', '\"', ',', '(', ')']
        punct_indexes = {}
        cur_word = ""
        word_list = []
        for i in range(len(input_str)):
            cur_symbol = input_str[i]
            if (cur_symbol in punctuation) or (
                    cur_symbol == '.' and (i == len(input_str) - 1 or input_str[i + 1] not in punctuation)):
                # (cur_symbol == '.' ... - точка, но не сокращение
                if len(cur_word) != 0:
                    word_list.append(cur_word.lower())
                    if cur_symbol != ' ':
                        punct_indexes[len(word_list) - 1] = cur_symbol
                    cur_word = ""
            elif cur_symbol != '-' or (len(cur_word) != 0):  # - и непустое слово -  это дефис
                cur_word = cur_word + cur_symbol
        if len(cur_word) != 0:
            word_list.append(cur_word.lower())

        s = ""
        for i in range(len(word_list)):
            s += word_list[i] + "_" + str(i) + " "
        return word_list, s[:-1] + input_str[-1], punct_indexes

    def get_punctuation_indexes(self):
        return self.punctuation_indexes

class HomogeneousGroup:
    def __init__(self, words: [str], title):
        self.words = words
        self.title = title

class TripleInfo:
    ''' Хранит разницу между родительской и дочерней точками разбора
        При переходе от root-точки разбора к точке разбора с одним разобранным словом считает main_pos=None, pattern=None
    '''
    def __init__(self, dep_pos, dep_var, main_pos=None, pattern=None):
        '''Хранится модель управления, номер главного слова и номер зависимого слова (и выбранного варианта разбора), к которым она применена'''
        self.main_position = main_pos
        self.dep_position = dep_pos
        self.dep_variant = dep_var
        self.pattern = pattern

    def get_dep_pos(self):
        return self.dep_position

    def get_dep_var(self):
        return self.dep_variant

class ParsePoint:
    direct_for_is_applicable = 1

    def __init__(self, pp_words:[WordInSentence], status: str,
                     point_number: int, parsed_words, link_words, potential_conjs,
                     sentence_info: SentenceInfo, difference: TripleInfo, parent_pp=None):
        self.pp_words = pp_words
        self.next_word_searcher = None
        self.status = status
        self.link_words = link_words # Словарь, номер_слова: [Gp]. Для связи главного слова и моделей управления, связанных с зависимым
        self.point_number = point_number # int
        self.parsed_words = parsed_words # set(int)
        self.potential_conjs = potential_conjs # set(int) TODO: в аннотацию типов
        self.view = None
        self.sentence_info = sentence_info  # TODO переделать! sentence_info лежит везде
        self.difference_from_parent = difference
        self.parent_pp = parent_pp

    def __eq__(self, other):
        if self.status != other.status:
            return False

        #Проверка, что в точках разбора одинаковое число слов
        if len(self.pp_words) != len(other.pp_words):
            return False

        #Проверка, что все слова одинаково разобраны
        for i in range(len(self.pp_words)):
            if self.pp_words[i] != other.pp_words[i]:
                return False

        #Проверка, что у точек разбора одинаковые связи между словами

            #Проверка, что у точек разбора одинаковый набор главных слов
        if set(self.link_words.keys()) != set(other.link_words.keys()):
            return False

        for main_word_ind in self.link_words.keys():
            self_dep = set()
            other_dep = set()
            for gp in self.link_words[main_word_ind]:
                dep_ind = gp.get_dep_word().get_number()
                self_dep.add(dep_ind)
            for gp in other.link_words[main_word_ind]:
                dep_ind = gp.get_dep_word().get_number()
                other_dep.add(dep_ind)
            if self_dep != other_dep: # Проверка, что для данного главного в обоих точках разбора одинаковый набор зависимых
                return False

        return True

    def is_dotted_children_created(self):
        return self.next_word_searcher is not None

    def is_final(self):
        return self.status == 'right' or self.status == 'right_with_conjs'

    def __repr__(self):
        ans = str(self.point_number) + ":"
        for main_ind, link_words in self.link_words.items():
            for link_word in link_words: # сейчас link_word - Gp
                ans += str(main_ind) + "+" + str(link_word.get_dep_word().get_number()) + ";"
        return ans

    def get_point_number(self):
        return self.point_number

    def set_view(self, view):
        self.view = view

    def index(self, word1):
        # ищет в списке слов в данной точке разбора индекс данного слова(класса Word), вспомогательная функция
        for i in range(len(self.pp_words)):
            if self.pp_words[i].word == word1:
                return i
        return None

    @staticmethod
    def check_inderect_dependency(self, number_main, number_dep):
        # dep_word = self.pp_words[number_dep]
        # main_word = self.pp_words[number_main]
        return True  # toDo ПЕРЕПИСАТЬ!!!!

    @staticmethod
    def check_is_word_in_dependent_group(self, number_main, number_dep):
        return True  # toDo ПЕРЕПИСАТЬ!!!!!

    def create_status(self):
        parsed_word_count = len(self.parsed_words)
        if parsed_word_count == len(self.pp_words):  # все слова разобраны
            # self.check_end_parse():
            if self.check_prep():
                self.status = 'right'
            else:
                self.status = 'wrong'
        else:
            unparsed_conjs = self.potential_conjs - self.parsed_words
            if len(unparsed_conjs) + parsed_word_count == len(self.pp_words):
                self.status = 'right_with_conjs'
                self.parse_conj()
            else:
                self.status = 'intermediate'

    def parse_conj(self):
        '''TODO Неразобранными остались только потенциальные союзы.
            Для каждого пот.союза создаем все возможные точки разбора, в которых он союз +
            точку разбора со всеми возможными несоюзными вариантами '''
        # Сейчас закрепляем первый союзный вариант разбора
        for conj_ind in self.potential_conjs - self.parsed_words:
            conj_variant_num = self.sentence_info.get_word_by_pos(conj_ind).first_conj_variant()
            self.pp_words[conj_ind].fix_morph_variant(conj_variant_num)

    def close(self):
        if self.status == 'intermediate':
            self.status = 'intermediate-close'


    def create_first_pp(self, first_word_pos: int, first_word_var: int, max_point_number: int):
        '''Создает точку разбора с одним разобранным словом'''
        new_pp_words = copy.deepcopy(self.pp_words)
        new_pp_words[first_word_pos].fix_morph_variant(first_word_var)

        new_point_number = max_point_number + 1
        new_parsed_words = set([first_word_pos])
        new_link_words = {i:[] for i in range(len(self.pp_words))}
        new_potential_conjs = copy.deepcopy(self.potential_conjs)
        difference = TripleInfo(dep_pos=first_word_pos, dep_var=first_word_var)
        new_parse_point = ParsePoint(pp_words=new_pp_words, status=self.status, point_number=new_point_number,
                                     parsed_words=new_parsed_words, link_words=new_link_words,
                                     potential_conjs=new_potential_conjs, sentence_info=self.sentence_info, difference=difference, parent_pp=self)

        main_word = new_parse_point.pp_words[first_word_pos]
        new_view = self.view.create_child_view(new_parse_point, main_word)
        new_parse_point.set_view(new_view)
        new_parse_point.create_status()
        return new_parse_point

    def create_dotted_edges_from_first_pp(self, first_pos: int, first_variant: int, all_wordforms: [(int, int)]):
        '''Создает ребра от точки разбора root.
        Выписываются тройки (разобранное слово, неразобранное слово, модель управления), применимые в данной точке разбора'''

        #first_pos, first_variant - первая разобранная словоформа
        self.next_word_searcher = NextWordSearcher(self.sentence_info, [],
                                                  first_pos, first_variant, all_wordforms)

    def find_first_word(self, fun, sentence_info):
        '''Среди слов предложения ищет варианты разбора, удовлетворяющие требованиям (например, глагольным и тп).
        Создает для каждого подходящего варианта разбора такие точки разбора, в которых для этого слова закреплен этот вариант разбора.
        В этих точках разбора разобрано ровно одно слово'''
        max_point_number = self.point_number
        list_new_parse_points = []
        for word_position in range(len(self.pp_words)):
            cur_point_word_forms = sentence_info.get_word(self.pp_words[word_position]).get_forms()
            for variant_number in range(len(cur_point_word_forms)):
                cur_morph = cur_point_word_forms[variant_number].morph
                if fun(cur_morph):
                    new_parse_point = self.create_first_pp(word_position, variant_number, max_point_number)
                    all_wordforms = [(i, j) for i in range(sentence_info.get_count_of_words())
                              for j in range(len(sentence_info.get_word_by_pos(i).forms))]
                    new_parse_point.create_dotted_edges_from_first_pp(word_position, variant_number, all_wordforms)
                    max_point_number += 1
                    list_new_parse_points.append(new_parse_point)
        return list_new_parse_points

    def find_best_gp(self):
        return self.next_word_searcher.next()

    def create_dotted_edges(self):
        '''Выписываются тройки (разобранное слово, неразобранное слово, модель управления), применимые в данной точке разбора'''
        #new_word_pos, new_dep_variant - разобранная словоформа, на которую точка разбора отличается от родительской
        parent_point = self.parent_pp
        last_parsed_word_pos = self.difference_from_parent.get_dep_pos()
        last_parsed_word_var = self.difference_from_parent.get_dep_var()
        self.next_word_searcher = NextWordSearcher(self.sentence_info, parent_point.next_word_searcher.triples,
                                                  last_parsed_word_pos, last_parsed_word_var,
                                                  parent_point.next_word_searcher.unparsed_wordforms)


    def create_child_parse_point(self, count_of_unroot_parse_points, main_pp_word_pos, g_pattern_to_apply, depending_pp_word_pos, dep_variant):
        """create and return new child ParsePoint"""

        new_pp_words = copy.deepcopy(self.pp_words)
        new_pp_words[depending_pp_word_pos].fix_morph_variant(dep_variant)

        new_point_number = count_of_unroot_parse_points + 1

        new_parsed_words = copy.deepcopy(self.parsed_words)
        new_parsed_words.add(depending_pp_word_pos)

        new_link_words = copy.deepcopy(self.link_words)
        new_gp = Gp(g_pattern_to_apply, new_pp_words[depending_pp_word_pos])
        new_link_words[main_pp_word_pos].append(new_gp)

        new_potential_conjs = copy.deepcopy(self.potential_conjs)

        new_view = copy.deepcopy(self.view)

        # TODO сначала вместо view - None, потом ставим его вручную...
        difference = TripleInfo(dep_pos=depending_pp_word_pos, dep_var=dep_variant, main_pos=main_pp_word_pos, pattern=g_pattern_to_apply)
        new_parse_point = ParsePoint(pp_words=new_pp_words, status=self.status,
                                     point_number=new_point_number, parsed_words=new_parsed_words, link_words=new_link_words,
                                     potential_conjs=new_potential_conjs, sentence_info=self.sentence_info, difference=difference, parent_pp=self)

        dep_word = new_parse_point.pp_words[depending_pp_word_pos]
        main_word = new_parse_point.pp_words[main_pp_word_pos]
        new_view = self.view.create_child_view(new_parse_point, main_word, dep_word)
        new_parse_point.set_view(new_view)
        new_parse_point.create_status()

        if new_parse_point.is_final():
            homogeneous_nodes = new_parse_point.merge_homogeneous(self.sentence_info.get_punctuation_indexes())
            new_parse_point.view.merge_homogeneous(homogeneous_nodes)

        # word_pair_text = str(g_pattern_to_apply.get_mark()) + ": " + str(main_pp_word_pos) + " + " + str(depending_pp_word_pos)
        word_pair_text = self.sentence_info.get_word(main_word).get_text() + " + " + self.sentence_info.get_word(
            dep_word).get_text()
        return new_parse_point, g_pattern_to_apply, word_pair_text

    def check_end_parse(self):
        """check that all words in this ParsePoint are parsed"""
        # если неразобранными остались только потенциальные союзы, то можно заканчивать, а может, и нет
        # TODO неразобранные союзы могут быть и союзами, и нет
        for cur_point_word in self.pp_words:
            if not cur_point_word.parsed:
                if next((x for x in cur_point_word.word.forms if x.morph.s_cl == 'conjunction'), None) is not None:
                    # один из вариантов разбора неразобранного слова - союз
                    continue
                else:
                    return False  # у неразобранного слова нет варианта разбора-союза
        return True

    def check_prep(self):
        for i in range(len(self.pp_words)):
            cur_main = self.pp_words[i]
            links_with_dep = self.link_words[i] # список связей главного слова с зависимыми
            if cur_main.is_parsed():
                main_morph = self.sentence_info.get_form_info(cur_main).get_morph()
                if main_morph.is_preposition():
                    if not links_with_dep:  # у предлога нет зависимого
                        return False
                    if len(links_with_dep) > 1:  # у предлога больше одного зависимого
                        return False
                    cur_dep = links_with_dep[0].dep_word
                    if cur_dep.number_in_sentence <= i:  # у предлога зависимое должно стоять справа от главного
                        return False
        return True

    def verb_has_homogeneous_subject(self):
        # если у глагола есть два зависимых именной части речи (сущ, прил и тп) И.п, то это однородн.подлежащие
        for i in range(len(self.pp_words)):
            cur_main = self.pp_words[i]
            if cur_main.is_parsed():
                main_morph = self.sentence_info.get_form_info(cur_main).get_morph()
                count_subject = 0
                if main_morph.is_verb():
                    links_with_dep = self.link_words[i] # список связей данного главного слова с зависимыми
                    for cur_gp in links_with_dep:
                        dep_word = cur_gp.dep_word
                        if dep_word.is_parsed():
                            dep_morph = self.sentence_info.get_form_info(dep_word).get_morph()
                            if dep_morph.is_noun_or_adj():
                                if dep_morph.is_nominative():
                                    count_subject += 1
                                    if count_subject > 1:
                                        return True
        return False

    def find_descendants(self):
        descendants = {}
        for i in range(len(self.pp_words)):
            links_with_dep = self.link_words[i]
            main = self.pp_words[i]
            descendants[main] = set(map(lambda x: x.dep_word, links_with_dep))
        changes = -1
        while changes != 0:
            changes = 0
            for node in descendants:
                old_count = len(descendants[node])
                for d in list(descendants[node]):
                    descendants[node] |= descendants[d]
                changes += len(descendants[node]) - old_count
        return descendants

    def create_homogeneous_title(self, homogeneous: [Gp], descendants,
                                 punctuation_indexes: [WordInSentence]): #descendants: {WordInSentence: set(WordInSentence)}
        words = self.sentence_info.get_word_texts()
        for ind in range(len(homogeneous)):
            h = homogeneous[ind].dep_word
            for d in descendants[h]:
                words[d.number_in_sentence] = str(ind)
            words[h.number_in_sentence] = str(ind)
        title = ''
        for i in range(len(words)):
            title += words[i]
            if i in punctuation_indexes:
                title += punctuation_indexes[i]
            else:
                title += " "
        return re.match('\D*(\d.*\d)\D*', title).groups()[0]

    def merge_homogeneous(self, punctuation_indexes):
        descendants = self.find_descendants() #{WordInSentence: set(WordInSentence)}
        comp_fun = lambda x: self.sentence_info.get_word(x.dep_word).get_forms()[
            x.dep_word.used_morph_answer].morph.get_homogeneous_params()
        homogeneous_nodes = []
        for main_ind in range(len(self.pp_words)):
            used_gp = self.link_words[main_ind] #[Gp]
            main = self.pp_words[main_ind]
            for key, group_items in groupby(sorted(used_gp, key=comp_fun), key=comp_fun):
                group_items_list = sorted(list(group_items), key=lambda x: x.dep_word.number_in_sentence) #[Gp]
                # key - ('noun', 'nominative', 'prep_type_any')
                # group_items_list - список из Gp, отсортированных по номеру в предложении
                if len(group_items_list) > 1:
                    title = self.create_homogeneous_title(group_items_list, descendants, punctuation_indexes)
                    dep_word_texts = [self.sentence_info.get_text(gp.get_dep_word()) for gp in group_items_list]
                    h = HomogeneousGroup(dep_word_texts, title)
                    main_text = self.sentence_info.get_text(main)
                    homogeneous_nodes.append((main_text, h))
        return homogeneous_nodes

    def create_first_parse_points(self, sentence_info):
        '''Из начальной root-вершины строит точки разбора с одним разобранным словом'''
        verb_res = self.find_first_word(lambda m: m.s_cl == 'verb', sentence_info)
        if verb_res:
            list_new_parse_points = verb_res
        else:
            # в предложении нет глагола
            noun_res = \
                self.find_first_word(lambda m: m.s_cl == 'noun' and m.case_morph == 'nominative', sentence_info)
            if noun_res:
                list_new_parse_points = noun_res
            else:
                prep_res = self.find_first_word(lambda m: m.s_cl == 'preposition', sentence_info)
                if prep_res:
                    list_new_parse_points = prep_res
                else:
                    print("В предложении нет глагола, сущ в И.п, предлога")
                    sys.exit()
        return list_new_parse_points

class Tree:
    '''Хранится дерево точек разбора'''
    def __init__(self, input_str):
        self.sentence_info = SentenceInfo(input_str)

        root_p_p = self.create_root_pp(self.sentence_info, self.sentence_info.get_sent_title_with_numbers())
        self.last_created_point = root_p_p # последняя созданная точка
        self.view = ParsePointTreeView(self.sentence_info.get_sent_title_with_numbers(), root_p_p.view)

        self.graph = nx.DiGraph()
        self.graph.add_node(0)
        self.graph_id_parse_point = {0: root_p_p}

        pps_with_one_parsed_word = root_p_p.create_first_parse_points(self.sentence_info) # [ParsePoint]

        for new_parse_point in pps_with_one_parsed_word:
            self.add_new_parse_point_into_graph(root_p_p, new_parse_point, None, "Разбор первого слова")
            self.view.add_edge(root_p_p.view, new_parse_point.view) # TODO избыточное создание еще одного графа...
        # описывает очередность точек разбора для построения дочерних точек разбора
        # есть корневая точка и len(list_new_parse_points) ее дочерних
        self.best_parse_points = self.create_best_parse_points(pps_with_one_parsed_word)

    def create_best_parse_points(self, pps_with_one_parsed_words):
        '''инициализируется список лучших для разбора точек'''
        # TODO переделать
        #  пока в список лучших для разбора точек кладем точки разбора с одним разобранным словом
        return copy.deepcopy(pps_with_one_parsed_words)

    def create_root_pp(self, sentence_info: SentenceInfo, sent_title: str): # TODO убрать sentence_info, сделать words
        words = sentence_info.get_words()
        pp_words = []  # [WordInSentence]
        potential_conjs = set()
        for word_number in range(len(words)):
            if words[word_number].first_conj_variant() is not None:  # у слова есть вариант разбора - союз
                potential_conjs.add(word_number)
            pp_words.append(WordInSentence(word_number))
        link_words = {i:[] for i in range(len(pp_words))}
        pp = ParsePoint(pp_words=pp_words, status='intermediate',
                        point_number=0, parsed_words=set(), link_words=link_words, potential_conjs=potential_conjs,
                        sentence_info=sentence_info, difference=None)
        # Из root_pp пунктирные ребра не проводятся.
        # Они сразу строятся, как невыбранные сплошные ребра, соединяющие root и ТР с одним разобранным словом
        view = ParsePointView('root', sent_title, sentence_info, len(pp_words))
        pp.set_view(view)
        return pp

    def get_best_parse_point(self):
        if len(self.best_parse_points) == 0:
            return None
        return self.best_parse_points[0]

    def close_best_point(self):
        '''Для первой точки разбора из списка лучших построены все дочерние точки разбора. С ней больше ничего нельзя сделать, удаляем ее.'''
        self.best_parse_points[0].close()
        self.view.close_node(self.best_parse_points[0].view.point_label)
        self.best_parse_points.pop(0)

    def insert_new_parse_point_in_best_points(self, new_point):
        '''Вставка только что построенной точки разбора в очередь на построение из точки разбора дочерних точек разбора'''
        # TODO сделать вариативность. Сейчас идем от новой точки разбора. Стратегия поиска в глубину
        self.best_parse_points.insert(0, new_point)

    def add_new_parse_point_into_graph(self, parent_point: ParsePoint, child_point: ParsePoint, pattern: GPattern, word_pair_text: str):
        '''Добавляет в граф новую точку разбора'''
        if pattern is None:
            # разбор первого слова в точке разбора, модель управления не была применена
            pattern_mark = 0
        else:
            # TODO надо сделать вычисление оценки на основе непроективности, расстояние между словами и оценки МУ
            pattern_mark = -(50 + pattern.get_mark())
            self.view.add_edge(parent_point.view, child_point.view, pattern, word_pair_text)

        self.graph.add_node(child_point.point_number)
        self.graph.add_edge(parent_point.point_number, child_point.point_number, weight=pattern_mark)
        self.graph_id_parse_point[child_point.point_number] = child_point
        self.last_created_point = child_point

    def get_word_parsing_variant(self, word: WordInSentence):
        return self.sentence_info.get_word_parsing_variant(word)

    def get_text(self, word: WordInSentence):
        return self.sentence_info.get_text(word)

    def choose_edge_from_pp(self, parent_point):
        '''В графе выбираем новое ребро, которое войдет в оптимальный путь. Из данной точки строим лучшее ребро'''
        res1 = parent_point.find_best_gp()
        if res1 is None:
            self.close_best_point() # TODO убрать!
            self.last_created_point = None
        else:
            main_word_pos, g_pattern_to_apply, dep_word_pos, dep_variant = res1
            count_of_unroot_parse_points = len(
                self.graph.nodes) - 1  # root - нулевая точка разбора и еще несколько точек разбора с одним разобранным словом
            res2 = parent_point.create_child_parse_point(count_of_unroot_parse_points=count_of_unroot_parse_points,
                                                             main_pp_word_pos=main_word_pos,
                                                             g_pattern_to_apply=g_pattern_to_apply,
                                                             depending_pp_word_pos=dep_word_pos,
                                                             dep_variant=dep_variant)

            (new_point, pattern, word_pair_text) = res2
            self.add_new_parse_point_into_graph(parent_point, new_point, pattern, word_pair_text)
            self.insert_new_parse_point_in_best_points(self.last_created_point) # TODO убрать. Сделать полноценный выбор точки разбора

    def sint_parse(self):
        begin_time = timer()
        while timer() - begin_time <= MAX_PARSING_TIME:
            best_parse_point = self.get_best_parse_point()
            if best_parse_point is None:  # Больше разборов нет
                return None

            if not best_parse_point.is_dotted_children_created():
                best_parse_point.create_dotted_edges()

            self.choose_edge_from_pp(best_parse_point)

            if self.last_created_point is not None and self.last_created_point.is_final():
                return self.last_created_point

            if self.last_created_point is not None:
                self.last_created_point.create_dotted_edges()

        raise StopIteration