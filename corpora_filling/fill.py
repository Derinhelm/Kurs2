import os
import pickle

import psycopg2
import pymorphy2

from corpora_filling.db_functions import *
from corpora_filling.extract_pairs_of_words import get_pairs
from timeit import default_timer as timer
import traceback

corporaToImpMorph = {'V': 's_cl', 'NUM': 's_cl', 'PR': 's_cl', 'A': 's_cl',
                     'ADV': 's_cl', 'CONJ': 's_cl', 'S': 's_cl', 'PART': 's_cl',
                     'ДЕЕПР': 's_cl', 'ПРИЧ': 's_cl', 'КР': 's_cl', 'СРАВ': 's_cl', 'INTJ': 's_cl',
                     'ПРЕВ': 's_cl',
                     'НЕОД': 'animate', 'ОД': 'animate',
                     'СРЕД': 'gender', 'МУЖ': 'gender', 'ЖЕН': 'gender',
                     'ЕД': 'number', 'МН': 'number',
                     'ИМ': 'case_morph', 'РОД': 'case_morph', 'ДАТ': 'case_morph',
                     'ВИН': 'case_morph', 'ТВОР': 'case_morph', 'ПР': 'case_morph', 'МЕСТН': 'case_morph',
                     'ПАРТ': 'case_morph',
                     'НЕСОВ': 'perfective', 'СОВ': 'perfective',
                     '3-Л': 'person', '2-Л': 'person', '1-Л': 'person',
                     'ПРОШ': 'tense', 'НАСТ': 'tense', 'НЕПРОШ': 'tense', 'ИНФ': 'tense',
                     'ИЗЪЯВ': 'tense', 'ПОВ': 'tense',
                     'СТРАД': 'voice'}

morph_analyzer = pymorphy2.MorphAnalyzer()



class Transformators: # для хранения словарей-отображений.
    def __init__(self, con, cursor):
        self.morphology_to_patterns = {} # Словарь для быстрой трансформации тега СинТагРуса в морфологические требования
        # (главное_слово, главная_лексема, тег_главного_из_синтагрус, зависимое_слово, зависимая_лексема, тег_зависимого_из_синтагрус) ->
        # -> морфологические характеристики главного и зависимого слова в соответствующие требования на главное/зависимое слова модели управления

        self.lexeme_to_lexeme_id = {} # лексема -> id лексемы в базе данных
        self.morph_constraints_to_id = {} # морфологические ограничения -> id морфологических ограничений в базе данных
        # например, (('s_cl','noun), ('animate', 'unanimate'), ('gender','neuter'), ('number','plural'), ('case_morph', 'genitive')) -> 5

        self.con = con
        self.cursor = cursor

    def transform_tags_to_morph_constraints(self, main_word: str, main_lexeme: str, main_morph_tag: str, dep_word: str, dep_lexeme: str, dep_morph_tag: str):
        '''На выходе: ((('s_cl','verb'),...), (('s_cl','noun'),...))'''
        if (main_word, main_lexeme, main_morph_tag, dep_word, dep_lexeme, dep_morph_tag) in self.morphology_to_patterns:
            return self.morphology_to_patterns[(main_word, main_lexeme, main_morph_tag, dep_word, dep_lexeme, dep_morph_tag)]
        else:
            main_res = get_parse_by_pymorphy(main_word, main_lexeme, main_morph_tag)
            dep_res = get_parse_by_pymorphy(dep_word, dep_lexeme, dep_morph_tag)
            if main_res is None or dep_res is None: # тег какой-то из словоформ не удалось разобрать
                return (None, None)
            main_morph, main_imp_features = main_res
            dep_morph, dep_imp_features = dep_res
            main_morph_constraints = create_constraints(main_morph, main_imp_features) # TODO: Может, делать создание требований на модель управления вместе
            dep_morph_constraints = create_constraints(dep_morph, dep_imp_features)

            self.morphology_to_patterns[(main_word, main_lexeme, main_morph_tag, dep_word, dep_lexeme, dep_morph_tag)] = (main_morph_constraints, dep_morph_constraints)
            return (main_morph_constraints, dep_morph_constraints)

    def transform_lexeme_to_db_id(self, lexeme: str):
        if lexeme in self.lexeme_to_lexeme_id:
            return self.lexeme_to_lexeme_id[lexeme]
        else:
            lexeme_id = find_or_insert_word(lexeme, self.con, self.cursor)
            self.lexeme_to_lexeme_id[lexeme] = lexeme_id
            return lexeme_id

    def transform_morph_constraints_to_db_id(self, morph_constraints):
        '''morph_constraints - (('s_cl', 'adjective'), ('gender', 'male'), ('number', 'single'), ('case_morph', 'instrumental'))'''
        if morph_constraints in self.morph_constraints_to_id:
            return self.morph_constraints_to_id[morph_constraints]
        else:
            morph_id = find_or_insert_morph_constraints(morph_constraints, self.con, self.cursor)
            self.morph_constraints_to_id[morph_constraints] = morph_id
            return morph_id

    def save_to_file(self, file_title):
        with open(file_title, 'wb') as f:
            pickle.dump((self.morphology_to_patterns, self.morph_constraints_to_id, self.lexeme_to_lexeme_id), f)

    def get_dicts_from_file(self, file_title):
        with open(file_title, 'rb') as f:
            (self.morphology_to_patterns, self.morph_constraints_to_id, self.lexeme_to_lexeme_id) = pickle.load(f)

def parse_corpora_tag(tag_corpora):
    # возвращает 1. список лямбда-функций, которые надо применить к морфу для проверки на адекватность
    # 2. set важных параметров
    check_funs = []
    imp_features = set()
    for cur_param in tag_corpora:
        if cur_param == 'V':
            check_funs.append(
                lambda m: m.s_cl in ['verb', 'participle', 'shortparticiple', 'gerund', 'frequentativeverb',
                                     'unpersonalverb', 'predicative'])
            imp_features.add('transitive')
        elif cur_param == 'S':
            check_funs.append(lambda m: m.s_cl in ['noun', 'pronoun', 'personalpronoun', 'name', 'pronounadjective',
                                                   'reflexivepronoun', 'comparative', 'predicative'])
        elif cur_param == 'A':
            check_funs.append(
                lambda m: m.s_cl in ['adjective', 'shortadjective', 'number', 'pronoun', 'reflexivepronoun',
                                     'pronounadjective', 'possesiveadjective', 'comparative', 'predicative'])
        # прилагательное: новый, мой, второй
        elif cur_param == 'ADV':
            check_funs.append(lambda m: m.s_cl in ['adverb', 'pronoun', 'comparative', 'predicative'])
        # наречие: плохо, отчасти
        elif cur_param == 'NUM':
            # числительное: пять, 2,
            check_funs.append(lambda m: m.s_cl in ['number', 'numberordinal', 'numberone', 'numbertwo', 'numberthree',
                                                   'numberbiform'])
        elif cur_param == 'PR':
            check_funs.append(lambda m: m.s_cl in ['preposition'])
            imp_features.add('prep_type')
        # предлог: в, между, вопреки
        elif cur_param == 'CONJ':
            check_funs.append(lambda m: m.s_cl in ['conjunction', 'pronoun'])
        # союз: и, что, как
        elif cur_param == 'PART':
            check_funs.append(lambda m: m.s_cl in ['particle'])
        # частица: бы, ли, только
        elif cur_param == 'INTJ':
            check_funs.append(lambda m: m.s_cl in ['interjection'])
        # междометие: ого, увы, эх
        elif cur_param == 'ИМ':
            check_funs.append(lambda m: m.case_morph == 'nominative')
        elif cur_param == 'РОД':
            check_funs.append(lambda m: m.case_morph == 'genitive')
        elif cur_param == 'ДАТ':
            check_funs.append(lambda m: m.case_morph == 'dative')
        elif cur_param == 'ВИН':
            check_funs.append(lambda m: m.case_morph == 'accusative')
        elif cur_param == 'ТВОР':
            check_funs.append(lambda m: m.case_morph == 'instrumental')
        elif cur_param == 'ПР':
            check_funs.append(lambda m: m.case_morph == 'prepositional')
        elif cur_param == 'ПАРТ':
            check_funs.append(lambda m: m.case_morph == 'genitive')
        elif cur_param == 'МЕСТН':
            check_funs.append(lambda m: m.case_morph == 'prepositional')
        elif cur_param == 'ЗВ':
            return None  # с звательным падежом пока не работаем

        elif cur_param == 'СРАВ':
            check_funs.append(lambda m: m.s_cl == 'comparative')
        elif cur_param == 'КР':
            check_funs.append(lambda m: m.s_cl == 'shortadjective' or m.s_cl == 'shortparticiple')
        elif cur_param == 'NID':
            return None

        elif cur_param == 'ЕД':
            check_funs.append(lambda m: m.number == 'single')
        elif cur_param == 'МН':
            check_funs.append(lambda m: m.number == 'plural')


        elif cur_param == 'МУЖ':
            check_funs.append(lambda m: m.gender == 'male')
        elif cur_param == 'ЖЕН':
            check_funs.append(lambda m: m.gender == 'female')
        elif cur_param == 'СРЕД':
            check_funs.append(lambda m: m.gender == 'neuter')

        elif cur_param == 'ОД':
            check_funs.append(lambda m: m.animate == 'animate' or m.animate == 'animate_any')
        elif cur_param == 'НЕОД':
            check_funs.append(lambda m: m.animate == 'unanimate' or m.animate == 'animate_any')

        if cur_param not in ['СЛ', 'COM', 'СМЯГ', 'НЕСТАНД', 'МЕТА', 'НЕПРАВ']:
            imp_features.add(corporaToImpMorph[cur_param])
    check_funs.append(lambda m: m.s_cl not in ['conjunction', 'particle', 'interjection'])
    if imp_features == set():
        return None  # нет меток, рассматриваемого вида
    return check_funs, imp_features


def eq_norm_form(s1, s2, parse_s2):
    # равенство начальных форм слов
    # parse_s2 - класс для превращения слова, разобранного в pymorphy2, в несов.вид
    if s1 == s2:
        return True
    if s1 == s2 + "ся":  # корпус убирает 'ся', pymorphy2 нет
        return True
    if s1.replace("ё", "е") == s2.replace("ё", "е"):
        return True
    s2_impf = parse_s2.inflect({'INFN', 'impf'})
    if s2_impf is not None and parse_s2.tag.POS == 'INFN' and s1 == s2_impf.word:
        # приводим второе слово в несов.вид
        # print(s1, s2)
        return True

    return False


def get_parse_by_pymorphy(cur_word, cur_normal_form, cur_tag_corpora):
    """return list of pairs (constraint_list, normal_form)"""
    if not check_word(cur_word):
        return None
    arr_parse = morph_analyzer.parse(cur_word)
    res_parse = parse_corpora_tag(cur_tag_corpora.split())
    if res_parse is None:  # слово типа NID, 'as-sifr'
        return None
    (check_funs, imp_features) = res_parse
    # print(cur_word, cur_tag_corpora, cur_normal_form, arr_parse)
    good_parse_pymorphy = []
    best_parse_pymorphy = None
    best_prob = 0
    for cur_parse in arr_parse:
        if eq_norm_form(cur_parse.normal_form, cur_normal_form, cur_parse) or \
                'НЕСТАНД' in cur_tag_corpora or 'НЕПРАВ' in cur_tag_corpora or \
                (('VERB' in cur_parse.tag or 'INFN' in cur_parse.tag or 'GRND' in cur_parse.tag or
                  'PRTF' in cur_parse.tag or 'PRTS' in cur_parse.tag) and cur_tag_corpora[0] == 'V'):
            # для глаголов пока не требуем совпадения начальных форм
            m = Morph(cur_parse, cur_word)
            nw = cur_parse.normal_form  # начальная форма слова
            prob = cur_parse.score
            if m is not None:
                flag_true_parse = True
                for cur_check_fun in check_funs:
                    if not cur_check_fun(m):
                        flag_true_parse = False
                        break
                if flag_true_parse:
                    if prob > best_prob:
                        best_prob = prob
                        best_parse_pymorphy = (m, imp_features)  # Если вдруг вараинтов разбора несколько, возвращаем самый вероятный (ооочень редкий случай)
                        good_parse_pymorphy.append((m, imp_features)) #TODO: убрать! Будет сильно замедлять (пока нужно, чтобы отследить, какие теги дают несколько вариантов)
    if len(good_parse_pymorphy) >= 2:
        print("Два варианта разбора:", (cur_word, cur_normal_form, cur_tag_corpora), good_parse_pymorphy)
    return best_parse_pymorphy


def insert_pattern3(con, cursor, main_morph_number, dep_morph_number,
                    main_word_number, dep_word_number, mark):
    command = "SELECT id FROM gpattern_3_level WHERE " + \
              "main_morph = %s AND dep_morph = %s AND " + \
              "main_word = %s AND dep_word = %s;"
    params = (main_morph_number, dep_morph_number,
              main_word_number, dep_word_number)
    cursor.execute(command, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        command = "INSERT INTO gpattern_3_level " + \
                  "VALUES(DEFAULT, %s, %s, %s, %s, " + str(mark) + ");"
        cursor.execute(command, params)
    else:
        number_gpattern = ind[0][0]
        command = "UPDATE gpattern_3_level " + \
                  "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(command, (number_gpattern,))
    con.commit()


def insert_pattern2(con, cursor, main_morph_number, dep_morph_number,
                    main_word_number, mark):
    command = "SELECT id FROM gpattern_2_level WHERE " + \
              "main_morph = %s AND dep_morph = %s AND " + \
              "main_word = %s;"
    params = (main_morph_number, dep_morph_number,
              main_word_number)
    cursor.execute(command, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        command = "INSERT INTO gpattern_2_level " + \
                  "VALUES(DEFAULT, %s, %s, %s, " + str(mark) + ");"
        cursor.execute(command, params)
    else:
        number_gpattern = ind[0][0]
        command = "UPDATE gpattern_2_level " + \
                  "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(command, (number_gpattern,))
    con.commit()


def insert_pattern1(con, cursor, main_morph_number, dep_morph_number, mark):
    command = "SELECT id FROM gpattern_1_level WHERE " + \
              "main_morph = %s AND dep_morph = %s;"
    params = (main_morph_number, dep_morph_number)
    cursor.execute(command, params)
    ind = cursor.fetchall()
    if len(ind) == 0:
        command = "INSERT INTO gpattern_1_level " + \
                  "VALUES(DEFAULT, %s, %s, " + str(mark) + ");"
        cursor.execute(command, params)
    else:
        number_gpattern = ind[0][0]
        command = "UPDATE gpattern_1_level " + \
                  "SET mark = mark + " + str(mark) + " WHERE id = %s;"
        cursor.execute(command, (number_gpattern,))
    con.commit()


def insert_pattern(con, cursor, main_morph_number, main_normal_form_number, dep_morph_number, dep_normal_form_number,
                   mark):
    insert_pattern3(con, cursor, main_morph_number, dep_morph_number,
                    main_normal_form_number, dep_normal_form_number, mark)
    insert_pattern2(con, cursor, main_morph_number, dep_morph_number,
                    main_normal_form_number, mark)
    insert_pattern1(con, cursor, main_morph_number, dep_morph_number, mark)


def check_word(word):
    if word is None:
        return False
    if word.count(" ") != 0:  # слова с пробелами пока не учитываем
        return False
    if '0' <= word[0] <= '9':
        return False
    return True


def create_constraints(morph, imp_features):
    variant_constraints = []
    for attr in imp_features:
        val = getattr(morph, attr)
        if val[-4:] != "_any":
            variant_constraints.append((attr, val))

    return tuple(variant_constraints) # tuple - тк потом будет использоваться как ключ словаря

if __name__ == '__main__':

    con = psycopg2.connect(dbname='gpatterns', user='postgres',
                     password='postgres', host='localhost')
    con.autocommit = False
    cursor = con.cursor()

    transformators = Transformators(con, cursor) # Словари для быстрой трансформации тега СинТагРуса в морфологические требования и тп
    if "processed_file_index.pickle" not in os.listdir():  # храним первую необработанный
        text_index = 0
    else:
        with open('processed_file_index.pickle', 'rb') as tf:
            text_index = pickle.load(tf)
        transformators.get_dicts_from_file('Transformators.pickle')

    pair_files = os.listdir("corpora_texts")
    first_unproc_file_index = text_index
    begin_time = timer()


    try:
        for file_ind in range(text_index, len(pair_files)):
            file_title = pair_files[file_ind]
            print(file_title, timer()-begin_time)
            pair_list = get_pairs('corpora_texts/' + file_title) # получаем список пар слов (не все из них - модели)
            # pair_list - Список вида ('инструкций', 'инструкция', 'S МН ЖЕН РОД НЕОД', 'описывающих', 'описывать', 'V НЕСОВ ПРИЧ НЕПРОШ МН РОД', 'corpora_texts/Algoritm.tgt', 1)

            text_corpora_labels = set()
            i = 0
            pair_len = len(pair_list)
            res = {}
            for (main_word, main_lexeme, main_morph_tag, dep_word, dep_lexeme, dep_morph_tag, _, _) in pair_list:
                (t_main_morph, t_dep_morph) = transformators.transform_tags_to_morph_constraints(main_word, main_lexeme, main_morph_tag, dep_word, dep_lexeme, dep_morph_tag)
                # морф.ограничения из корпуса -> морф.ограничения для бд
                if t_main_morph is not None and t_dep_morph is not None:
                    main_lexeme_id = transformators.transform_lexeme_to_db_id(main_lexeme)
                    dep_lexeme_id = transformators.transform_lexeme_to_db_id(dep_lexeme)
                    main_morph_id = transformators.transform_morph_constraints_to_db_id(t_main_morph)
                    dep_morph_id = transformators.transform_morph_constraints_to_db_id(t_dep_morph)
                    if (main_morph_id, main_lexeme_id, dep_morph_id, dep_lexeme_id) in res: # Для оптимищазации. Сначала собираем статистику по МУ для одного текста, потом вставляем все МУ из одного текста в базу
                        res[(main_morph_id, main_lexeme_id, dep_morph_id, dep_lexeme_id)] += 1
                    else:
                        res[(main_morph_id, main_lexeme_id, dep_morph_id, dep_lexeme_id)] = 1
                    if i % 100 == 0:
                        print(i, pair_len, sep=" / ")
                    i += 1

            for ((main_morph_id, main_lexeme_id, dep_morph_id, dep_lexeme_id), mark) in res.items():
                insert_pattern(con, cursor, main_morph_id, main_lexeme_id,
                               dep_morph_id, dep_lexeme_id, mark)

            # Выделили все модели управления из файла
            con.commit()
            transformators.save_to_file('Transformators.pickle')
            first_unproc_file_index += 1
    except KeyboardInterrupt as exc:
        with open('processed_file_index.pickle', 'wb') as f:
            pickle.dump(first_unproc_file_index, f)
            con.rollback()

    finally:
        cursor.close()
        con.close()