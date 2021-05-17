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


class Gp:
    def __init__(self, mod, dw):
        self.model = mod
        self.dep_word = dw


class WordInSentence:
    def __init__(self, number):
        self.parsed = False
        self.used_morph_answer = None  # номер варианта разбора для разобранных слов
        self.used_gp = []  # типа Gp
        self.number_in_sentence = number

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


class SentenceInfo:
    def __init__(self, words):
        self.words = words  # список элементов типа Word

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


class HomogeneousGroup:
    def __init__(self, words: WordInSentence, title):
        self.words = words
        self.title = title


class ParsePoint:
    direct_for_is_applicable = 1

    def __init__(self, pp_words, next_word_searcher, status,
                 parsed, point_number, parsed_words, potential_conjs, punctuations_ind, sentence_info):
        self.pp_words = pp_words
        self.next_word_searcher = next_word_searcher
        self.status = status
        self.parsed = parsed
        self.point_number = point_number
        self.parsed_words = parsed_words
        self.potential_conjs = potential_conjs
        self.punctuations_ind = punctuations_ind
        self.view = None
        self.sentence_info = sentence_info  # TODO переделать! sentence_info лежит везде

    def __repr__(self):
        ans = str(self.point_number) + ":"
        for i in self.parsed:
            ans += str(i[0]) + "+" + str(i[1]) + ";"
        return ans

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
            self.pp_words[conj_ind].fix_morph_variant(self.pp_words[conj_ind].word.first_conj_variant())

    def close(self):
        self.status = 'intermediate-close'

    def create_firsts_pp(self, main_pos, main_var, max_point_number):
        new_pp_words = copy.deepcopy(self.pp_words)
        new_pp_words[main_pos].fix_morph_variant(main_var)
        unparsed_wordforms = [(i, j) for i in range(self.sentence_info.get_count_of_words())
                              for j in range(len(self.sentence_info.get_word_by_pos(i).forms))]

        new_next_word_searcher = NextWordSearcher(self.sentence_info, [], main_pos, main_var, unparsed_wordforms)
        new_parsed = copy.deepcopy(self.parsed)
        new_point_number = max_point_number + 1
        new_parsed_words = set([main_pos])
        new_potential_conjs = copy.deepcopy(self.potential_conjs)
        new_parse_point = ParsePoint(pp_words=new_pp_words, next_word_searcher=new_next_word_searcher,
                                     status=self.status, parsed=new_parsed, point_number=new_point_number,
                                     parsed_words=new_parsed_words,
                                     potential_conjs=new_potential_conjs, punctuations_ind=self.punctuations_ind,
                                     sentence_info=self.sentence_info)

        main_word = new_parse_point.pp_words[main_pos]
        new_view = self.view.create_child_view(new_parse_point, main_word)
        new_parse_point.set_view(new_view)
        new_parse_point.create_status()
        return new_parse_point

    def find_first_word(self, fun):
        max_point_number = self.point_number
        list_new_parse_points = []
        for word_position in range(len(self.pp_words)):
            cur_point_word_forms = self.sentence_info.get_word(self.pp_words[word_position]).get_forms()
            for variant_number in range(len(cur_point_word_forms)):
                cur_morph = cur_point_word_forms[variant_number].morph
                if fun(cur_morph):
                    new_parse_point = self.create_firsts_pp(word_position, variant_number, max_point_number)
                    max_point_number += 1
                    list_new_parse_points.append(new_parse_point)
        return list_new_parse_points

    def create_child_parse_point(self, max_point_number):
        """create and return new child ParsePoint"""
        # print("------")
        att_res = self.next_word_searcher.next()
        if att_res is None:
            return None
        (main_pp_word_pos, g_pattern_to_apply, depending_pp_word_pos, dep_variant) = att_res

        new_pp_words = copy.deepcopy(self.pp_words)
        new_pp_words[depending_pp_word_pos].fix_morph_variant(dep_variant)

        new_next_word_searcher = NextWordSearcher(self.sentence_info, self.next_word_searcher.main_dep_pattern,
                                                  depending_pp_word_pos, dep_variant,
                                                  self.next_word_searcher.unparsed_wordforms)

        new_parsed = copy.deepcopy(self.parsed)
        new_parsed.append((main_pp_word_pos, depending_pp_word_pos))
        new_point_number = max_point_number + 1

        new_parsed_words = copy.deepcopy(self.parsed_words)
        new_parsed_words.add(depending_pp_word_pos)
        new_potential_conjs = copy.deepcopy(self.potential_conjs)

        new_view = copy.deepcopy(self.view)

        # punctuations_ind - общее, тк пунктуация общая, 
        # TODO сначала вместо view - None, потом ставим его вручную...

        new_parse_point = ParsePoint(pp_words=new_pp_words, next_word_searcher=new_next_word_searcher,
                                     status=self.status,
                                     parsed=new_parsed, point_number=new_point_number, parsed_words=new_parsed_words,
                                     potential_conjs=new_potential_conjs, punctuations_ind=self.punctuations_ind,
                                     sentence_info=self.sentence_info)

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
                print(type(cur_point_word.word.forms[0].morph.s_cl))
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

    def create_homogeneous_title(self, homogeneous, descendants):
        words = [w.word.word_text for w in self.pp_words]
        for ind in range(len(homogeneous)):
            h = homogeneous[ind].dep_word
            for d in descendants[h]:
                words[d.number_in_sentence] = str(ind)
            words[h.number_in_sentence] = str(ind)
        title = ''
        for i in range(len(words)):
            title += words[i]
            if i in self.punctuations_ind:
                title += self.punctuations_ind[i]
            else:
                title += " "
        return re.match('\D*(\d.*\d)\D*', title).groups()[0]

    def merge_homogeneous(self):
        descendants = self.find_descendants()
        comp_fun = lambda x: self.sentence_info.get_word(x.dep_word).get_forms()[
            x.dep_word.used_morph_answer].morph.get_homogeneous_params()
        new_used_gp = []
        homogeneous_nodes = []
        for main in self.pp_words:
            for key, group_items in groupby(sorted(main.used_gp, key=comp_fun), key=comp_fun):
                group_items_list = sorted(list(group_items), key=lambda x: x.dep_word.number_in_sentence)
                if len(group_items_list) > 1:
                    title = self.create_homogeneous_title(group_items_list, descendants)
                    h = HomogeneousGroup(group_items_list, title) #TODO исправить!
                    new_used_gp.append(h)
                    homogeneous_nodes.append((main, h))
                else:
                    new_used_gp.append(group_items_list)
        main.used_gp = new_used_gp # TODO что это?
        return homogeneous_nodes


class Sentence:
    def __init__(self, input_str):
        self.best_parse_points = []  # хранится список точек разбора, упорядоченных по убыванию оценки
        self.max_number_parse_point = 0

        word_list, sent_title, punctuatuon_ind = self.split_string(input_str)
        self.sent_title_numb = sent_title
        self.sent_title_without_numb = input_str
        self.punctuatuon_ind = punctuatuon_ind  # индексы,
        con = psycopg2.connect(dbname='gpatterns', user='postgres',
                               password='postgres', host='localhost', port='5433')
        morph_analyzer = pymorphy2.MorphAnalyzer()
        self.root_p_p, self.sentence_info = self.create_root_pp(word_list, con, morph_analyzer,
                                                                self.sent_title_without_numb, self.punctuatuon_ind)
        self.view = ParsePointTreeView(self.sent_title_numb, self.root_p_p.view)
        self.graph = nx.DiGraph()
        self.graph.add_node(0)
        self.graph_id_parse_point = {0: self.root_p_p}
        self.create_first_parse_points()
        con.close()


    def __repr__(self):
        return self.sent_title_without_numb

    def create_root_pp(self, word_texts, con, morph_analyzer, sent_title, punctuations_ind):
        pp_words = []  # [WordInSentence]
        words = []  # [Word]
        potential_conjs = set()
        for number in range(len(word_texts)):
            word_info = Word(con, morph_analyzer, word_texts[number])
            words.append(word_info)
            if word_info.first_conj_variant() is not None:  # у слова есть вариант разбора - союз
                potential_conjs.add(number)
            pp_words.append(WordInSentence(number))
        sentence_info = SentenceInfo(words)
        pp = ParsePoint(pp_words=pp_words, next_word_searcher=None, status='intermediate', parsed=[],
                        point_number=0, parsed_words=set(), potential_conjs=potential_conjs,
                        punctuations_ind=punctuations_ind,
                        sentence_info=sentence_info)
        view = ParsePointView('root', sent_title, sentence_info, len(pp_words))
        pp.set_view(view)
        return pp, sentence_info

    def get_word_parsing_variant(self, word: WordInSentence):
        return self.sentence_info.get_form_info(word)

    def get_text(self, word: WordInSentence):
        return self.sentence_info.get_text(word)

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
        for i in range(len(list_new_parse_points)):
            new_point_id = i + 1
            self.graph.add_node(new_point_id)
            self.graph.add_edge(0, new_point_id)
            child_point = list_new_parse_points[i]
            self.graph_id_parse_point[new_point_id] = child_point
            self.view.add_edge(self.root_p_p.view, child_point.view)
        self.max_number_parse_point = len(list_new_parse_points)
        # есть корневая точка и len(list_new_parse_points) ее дочерних,
        self.best_parse_points = copy.deepcopy(list_new_parse_points)

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
        begin_time = timer()
        while True:
            d = timer() - begin_time
            # print(d)
            if d > 60:
                return "timeEnd"  # toDo не None !!!
            best_parse_point = self.get_best_parse_point()
            if best_parse_point is None:
                # print("Не разобрано!")
                return None
            res = best_parse_point.create_child_parse_point(self.max_number_parse_point)
            # print(res)
            if res is None:
                self.close_point()
                self.view.close_node(best_parse_point.view.point_label)
            else:
                (new_point, pattern, word_pair_text) = res
                self.graph.add_node(new_point.point_number)
                self.graph.add_edge(best_parse_point.point_number, new_point.point_number)
                self.graph_id_parse_point[new_point.point_number] = new_point
                self.max_number_parse_point += 1
                self.view.add_edge(best_parse_point.view, new_point.view, pattern, word_pair_text)
                if new_point.status == 'right' or new_point.status == 'right_with_conjs':
                    print(new_point.status)
                    homogeneous_nodes = new_point.merge_homogeneous()
                    new_point.view.merge_homogeneous(homogeneous_nodes)
                    return new_point
                else:
                    self.insert_new_parse_point(new_point)
