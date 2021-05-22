import copy
import sys
from timeit import default_timer as timer
from itertools import groupby

import networkx as nx
import psycopg2
import pymorphy2
import re

from next_word_search_module import NextWordSearcher
from patterns import GPattern
from visualize import ParsePointView, ParsePointTreeView
from word_module import Word

MAX_PARSING_TIME = 60

class WordInSentence:
    def __init__(self, number_in_sentence: int):
        self.parsed = False
        self.used_morph_answer = None  # номер варианта разбора для разобранных слов
        self.used_gp = []  # типа Gp
        self.number_in_sentence = number_in_sentence

    def __repr__(self):
        if self.parsed:
            return "word № " + str(self.number_in_sentence) + ", variant " + str(self.used_morph_answer)
        return "word № " + str(self.number_in_sentence) + " not_parsed"

    def __eq__(self, other):
        return self.number_in_sentence == other.number_in_sentence

    def __hash__(self):
        return self.number_in_sentence

    def fix_morph_variant(self, variant_position: int):
        """слово становится разобранным"""
        self.parsed = True
        self.used_morph_answer = variant_position

    def is_parsed(self):
        return self.parsed

    def add_gp(self, pattern: GPattern, dep_word):
        # dep_word - WordInSentence
        new_gp = Gp(pattern, dep_word)
        self.used_gp.append(new_gp)

class Gp:
    def __init__(self, mod: GPattern, dw: WordInSentence):
        self.model = mod
        self.dep_word = dw

    def get_dep_word(self):
        return self.dep_word

class SentenceInfo:
    '''Хранит информацию о вариантах разбора каждого слова из предложения.'''
    def __init__(self, input_str: str):
        word_texts, self.sent_title_with_numbers, self.punctuation_indexes = self.split_string(input_str)
        self.sent_title_without_numb = input_str
        con = psycopg2.connect(dbname='gpatterns', user='postgres',
                               password='postgres', host='localhost', port='5433')
        morph_analyzer = pymorphy2.MorphAnalyzer()
        self.words = []  # [Word]
        for word_text in word_texts:
            word_info = Word(con, morph_analyzer, word_text)
            self.words.append(word_info)
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

class ParsePoint:
    direct_for_is_applicable = 1

    def __init__(self, pp_words, status,
                 parsed, point_number, parsed_words, potential_conjs, sentence_info):
        self.pp_words = pp_words
        self.next_word_searcher = None
        self.status = status
        self.parsed = parsed
        self.point_number = point_number
        self.parsed_words = parsed_words
        self.potential_conjs = potential_conjs
        self.view = None
        self.sentence_info = sentence_info  # TODO переделать! sentence_info лежит везде


    def __repr__(self):
        ans = str(self.point_number) + ":"
        for i in self.parsed:
            ans += str(i[0]) + "+" + str(i[1]) + ";"
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
        self.status = 'intermediate-close'


    def create_first_pp(self, main_pos: int, main_var: int, max_point_number: int):
        '''Создает точку разбора с одним разобранным словом'''
        new_pp_words = copy.deepcopy(self.pp_words)
        new_pp_words[main_pos].fix_morph_variant(main_var)

        new_parsed = copy.deepcopy(self.parsed)
        new_point_number = max_point_number + 1
        new_parsed_words = set([main_pos])
        new_potential_conjs = copy.deepcopy(self.potential_conjs)
        new_parse_point = ParsePoint(pp_words=new_pp_words, status=self.status, parsed=new_parsed, point_number=new_point_number,
                                     parsed_words=new_parsed_words,
                                     potential_conjs=new_potential_conjs, sentence_info=self.sentence_info)

        main_word = new_parse_point.pp_words[main_pos]
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

    def create_dotted_edges(self, parent_point, new_word_pos, new_dep_variant):
        '''Выписываются тройки (разобранное слово, неразобранное слово, модель управления), применимые в данной точке разбора'''
        #new_word_pos, new_dep_variant - разобранная словоформа, на которую точка разбора отличается от родительской
        self.next_word_searcher = NextWordSearcher(self.sentence_info, parent_point.next_word_searcher.triples,
                                                  new_word_pos, new_dep_variant,
                                                  parent_point.next_word_searcher.unparsed_wordforms)


    def create_child_parse_point(self, count_of_unroot_parse_points, main_pp_word_pos, g_pattern_to_apply, depending_pp_word_pos, dep_variant):
        """create and return new child ParsePoint"""

        new_pp_words = copy.deepcopy(self.pp_words)
        new_pp_words[depending_pp_word_pos].fix_morph_variant(dep_variant)

        new_parsed = copy.deepcopy(self.parsed)
        new_parsed.append((main_pp_word_pos, depending_pp_word_pos))
        new_point_number = count_of_unroot_parse_points + 1

        new_parsed_words = copy.deepcopy(self.parsed_words)
        new_parsed_words.add(depending_pp_word_pos)
        new_potential_conjs = copy.deepcopy(self.potential_conjs)

        new_view = copy.deepcopy(self.view)

        # TODO сначала вместо view - None, потом ставим его вручную...

        new_parse_point = ParsePoint(pp_words=new_pp_words, status=self.status,
                                     parsed=new_parsed, point_number=new_point_number, parsed_words=new_parsed_words,
                                     potential_conjs=new_potential_conjs, sentence_info=self.sentence_info)

        new_parse_point.pp_words[main_pp_word_pos].add_gp(g_pattern_to_apply,
                                                          new_parse_point.pp_words[depending_pp_word_pos])
        dep_word = new_parse_point.pp_words[depending_pp_word_pos]
        main_word = new_parse_point.pp_words[main_pp_word_pos]
        new_view = self.view.create_child_view(new_parse_point, main_word, dep_word)
        new_parse_point.set_view(new_view)
        new_parse_point.create_status()

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
            if cur_main.is_parsed():
                main_morph = self.sentence_info.get_form_info(cur_main).get_morph()
                if main_morph.is_preposition():
                    if not cur_main.used_gp:  # у предлога нет зависимого
                        return False
                    if len(cur_main.used_gp) > 1:  # у предлога больше одного зависимого
                        return False
                    cur_dep = cur_main.used_gp[0].dep_word
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
                    for cur_gp in cur_main.used_gp:
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
        for main in self.pp_words:
            descendants[main] = set(map(lambda x: x.dep_word, main.used_gp))
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
        new_used_gp = []
        homogeneous_nodes = []
        for main in self.pp_words:
            for key, group_items in groupby(sorted(main.used_gp, key=comp_fun), key=comp_fun):
                group_items_list = sorted(list(group_items), key=lambda x: x.dep_word.number_in_sentence) #[Gp]
                if len(group_items_list) > 1:
                    title = self.create_homogeneous_title(group_items_list, descendants, punctuation_indexes)
                    dep_word_texts = [self.sentence_info.get_text(gp.get_dep_word()) for gp in group_items_list]
                    h = HomogeneousGroup(dep_word_texts, title)
                    new_used_gp.append(h)
                    main_text = self.sentence_info.get_text(main)
                    homogeneous_nodes.append((main_text, h))
                else:
                    new_used_gp.append(group_items_list)
            main.used_gp = new_used_gp
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

        self.view = ParsePointTreeView(self.sentence_info.get_sent_title_with_numbers(), root_p_p.view)

        self.graph = nx.DiGraph()
        self.graph.add_node(0)
        self.graph_id_parse_point = {0: root_p_p}

        pps_with_one_parsed_word = root_p_p.create_first_parse_points(self.sentence_info) # [ParsePoint]

        for new_parse_point in pps_with_one_parsed_word:
            self.add_new_parse_point_into_graph(root_p_p, new_parse_point)
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
        pp = ParsePoint(pp_words=pp_words, status='intermediate', parsed=[],
                        point_number=0, parsed_words=set(), potential_conjs=potential_conjs,
                        sentence_info=sentence_info)
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
        self.best_parse_points.pop(0)

    def insert_new_parse_point(self, new_point):
        '''Вставка только что построенной точки разбора в очередь на построение из точки разбора дочерних точек разбора'''
        # TODO сделать вариативность. Сейчас идем от новой точки разбора. Стратегия поиска в глубину
        self.best_parse_points.insert(0, new_point)

    def add_new_parse_point_into_graph(self, parent_point, child_point):
        '''Добавляет в граф новую точку разбора'''
        self.graph.add_node(child_point.point_number)
        self.graph.add_edge(parent_point.point_number, child_point.point_number)
        self.graph_id_parse_point[child_point.point_number] = child_point

    def get_word_parsing_variant(self, word: WordInSentence):
        return self.sentence_info.get_word_parsing_variant(word)

    def get_text(self, word: WordInSentence):
        return self.sentence_info.get_text(word)

    def sint_parse(self):
        begin_time = timer()
        while True:
            if timer() - begin_time > MAX_PARSING_TIME:
                return "timeEnd"  # toDo не None !!!
            best_parse_point = self.get_best_parse_point()
            if best_parse_point is None:  # Больше разборов нет
                return None
            res1 = best_parse_point.find_best_gp()
            if res1 is None:
                self.close_point()
                self.view.close_node(best_parse_point.view.point_label)
            else:
                main_pp_word_pos, g_pattern_to_apply, depending_pp_word_pos, dep_variant = res1
                count_of_unroot_parse_points = len(self.graph.nodes) - 1  # root - нулевая точка разбора и еще несколько точек разбора с одним разобранным словом
                res2 = best_parse_point.create_child_parse_point(count_of_unroot_parse_points=count_of_unroot_parse_points,
                        main_pp_word_pos=main_pp_word_pos, g_pattern_to_apply=g_pattern_to_apply,
                        depending_pp_word_pos=depending_pp_word_pos, dep_variant=dep_variant)
                (new_point, pattern, word_pair_text) = res2
                new_point.create_dotted_edges(best_parse_point, depending_pp_word_pos, dep_variant)
                self.add_new_parse_point_into_graph(best_parse_point, new_point)
                self.view.add_edge(best_parse_point.view, new_point.view, pattern, word_pair_text)
                if new_point.status == 'right' or new_point.status == 'right_with_conjs':
                    print(new_point.status)
                    homogeneous_nodes = new_point.merge_homogeneous(self.sentence_info.get_punctuation_indexes())
                    new_point.view.merge_homogeneous(homogeneous_nodes)
                    return new_point
                else:
                    self.insert_new_parse_point(new_point)