import pickle

import psycopg2
import pymorphy2

from dbFunctions import *
from word_module import WordForm

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


class DBWordInfo:
    def __init__(self, constraints_id, normal_form_id, prob):
        self.constraints_id = constraints_id
        self.normal_form_id = normal_form_id
        self.probability = prob  # TODO это не вероятность! переименовать!


def parse_corpora_tag(tag_corpora):
    # возвращает 1. список лямбда-функций, которые надо применить к морфу
    # для проверки на адекватность
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

        if cur_param not in ['СЛ', 'COM', 'СМЯГ', 'НЕСТАНД', 'МЕТА', 'НЕПРАВ']:
            imp_features.add(corporaToImpMorph[cur_param])
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


# f = open('mismatch_of_the_initial_form', 'w')

def get_parse_by_pymorphy(cur_word, cur_tag_corpora, cur_normal_form, arr_parse):
    """return list of pairs (morph, normal form)"""
    res_parse = parse_corpora_tag(cur_tag_corpora)
    if res_parse is None:  # слово типа NID, 'as-sifr'
        return None
    (check_funs, imp_features) = res_parse
    # print(cur_word, cur_tag_corpora, cur_normal_form, arr_parse)
    not_imp_feat = set(Morph.names) - imp_features
    good_parse_pymorphy = []
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
                    if m not in good_parse_pymorphy:
                        word_form = WordForm(m, nw, prob)
                        good_parse_pymorphy += [word_form]
    return good_parse_pymorphy, not_imp_feat


def delete_cpi_from_list(variants_list):
    """удаляем словосочетания с частицами, союзами, междометиями звательным падежем"""
    # variants_list - [WordForm]
    i = 0
    while i < len(variants_list):
        if variants_list[i].morph.s_cl in ['conjunction', 'particle', 'interjection'] or \
                variants_list[i].morph.case_morph == 'vocative':
            variants_list.pop(i)
        else:
            i += 1
    return variants_list


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


def insert_all_pairs(con, cursor, main_inserts, dep_inserts):
    # массив номеров слова в таблице word(мб несколько в дальнейшем)
    # пока массив из одного элемента
    denominator = 0
    for cur_main in main_inserts:
        for cur_dep in dep_inserts:
            denominator += cur_main.probability * cur_dep.probability
    for cur_main in main_inserts:
        for cur_dep in dep_inserts:
            main_morph_number = cur_main.constraints_id
            main_normal_form_number = cur_main.normal_form_id
            dep_morph_number = cur_dep.constraints_id
            dep_normal_form_number = cur_dep.normal_form_id
            mark = cur_main.probability * cur_dep.probability / denominator
            insert_pattern(con, cursor, main_morph_number, main_normal_form_number,
                           dep_morph_number, dep_normal_form_number, mark)


def check_word(word):
    if word is None:
        return False
    if word.count(" ") != 0:  # слова с пробелами пока не учитываем
        return False
    if '0' <= word[0] <= '9':
        return False
    return True


def create_constraints(variant, not_imp):
    variant_constraints_list = []
    for attr in Morph.names:
        if attr not in not_imp:
            val = getattr(variant.morph, attr)
            if val[-4:] != "_any":
                variant_constraints_list.append((attr, val))

    return variant_constraints_list


def create_db_numbers(variants, not_imp):
    """variant(WordForm) to list of constraints - [(номер ограничения в базе,номер слова)]"""
    constraints_list = []
    for variant in variants:
        cons_list = create_constraints(variant, not_imp)
        cons_id = find_or_insert_morph_constraints(cons_list, con, cursor)
        normal_form_id = find_or_insert_word(variant.normal_form, con, cursor)

        # ограничение на нач.форму слова(2 и 3 уровень)
        constraints_list.append(DBWordInfo(cons_id, normal_form_id, variant.probability))
    return constraints_list


def insert_pair(cur_pair, morph_analyzer: pymorphy2.MorphAnalyzer, con, cursor):
    (main_word, main_normal_form, main_feat, dep_word,
     dep_normal_form, dep_feat, _, _) = cur_pair
    if (not check_word(main_word)) or (not check_word(dep_word)):
        return
    dep_feat = dep_feat.split()
    main_feat = main_feat.split()
    dep_res = get_parse_by_pymorphy(dep_word, dep_feat, dep_normal_form, morph_analyzer.parse(dep_word))
    if dep_res is None:
        return
    (dep_variants, dep_not_imp) = dep_res
    main_res = get_parse_by_pymorphy(main_word, main_feat, main_normal_form,
                                     morph_analyzer.parse(main_word))
    if main_res is None:
        return
    (main_variants, main_not_imp) = main_res
    dep_variants = delete_cpi_from_list(dep_variants)
    main_variants = delete_cpi_from_list(main_variants)
    if dep_variants == [] or main_variants == []:
        return
    dep_constraints_numbers = create_db_numbers(dep_variants, dep_not_imp)
    main_constraints_numbers = create_db_numbers(main_variants, main_not_imp)

    insert_all_pairs(con, cursor, main_constraints_numbers, dep_constraints_numbers)


if __name__ == '__main__':
    # 610944- последняя сделанная в gpatterns_4 610945 - voct
    # 898384 - последняя в gpatterns
    morph_analyzer = pymorphy2.MorphAnalyzer()
    con = psycopg2.connect(dbname='gpatterns', user='postgres',
                           password='postgres', host='localhost')
    with open('pairsList.pickle', 'rb') as f:
        pairsList = pickle.load(f)
    for i in range(497413, len(pairsList)):
        print(i)
        cur_pair = pairsList[i]
        cursor = con.cursor()
        insert_pair(cur_pair, morph_analyzer, con, cursor)
        cursor.close()

'''file_name = 'tests/sochin.txt'
cur_pair_list = []
cur_pair_list = insert(file_name, file_name)
x = 0'''

'''
if __name__ == '__main__':
    pairs_list = []
    for i in range(len(name_files)):
        text_title = name_files[i]
        print("---------------------------------")
        print(i, text_title)
        allName = "all/" + text_title
        cur_pair_list = insert(allName, text_title)
        pairs_list += cur_pair_list
        print(len(pairs_list))

    with open('pairs_list.pickle', 'wb') as f:
        pickle.dump(pairs_list, f)
'''
