import os
import pickle

import psycopg2
import pymorphy2

from corpora_filling.db_functions import *
from corpora_filling.extract_pairs_of_words import get_pairs

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
con = psycopg2.connect(dbname='gpatterns', user='postgres',
                       password='postgres', host='localhost')


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
    if cur_word == 'должны':
        x = 0
    if not check_word(cur_word):
        return ()
    arr_parse = morph_analyzer.parse(cur_word)
    res_parse = parse_corpora_tag(cur_tag_corpora.split())
    if res_parse is None:  # слово типа NID, 'as-sifr'
        return ()
    (check_funs, imp_features) = res_parse
    # print(cur_word, cur_tag_corpora, cur_normal_form, arr_parse)
    not_imp_feat = set(Morph.names) - imp_features
    good_parse_pymorphy = ()
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
                        morph_constraints = create_constraints(m, not_imp_feat)
                        good_parse_pymorphy += ((morph_constraints, nw, prob),)
    return good_parse_pymorphy


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


Counter = 0


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
            mark = cur_main.probability * cur_dep.probability / denominator  # TODO логарифмировать
            insert_pattern(con, cursor, main_morph_number, main_normal_form_number,
                           dep_morph_number, dep_normal_form_number, mark)
    if len(main_inserts) == 0 or len(dep_inserts) == 0:
        global Counter
        Counter += 1


def check_word(word):
    if word is None:
        return False
    if word.count(" ") != 0:  # слова с пробелами пока не учитываем
        return False
    if '0' <= word[0] <= '9':
        return False
    return True


def create_constraints(morph, not_imp):
    variant_constraints = ()
    for attr in Morph.names:
        if attr not in not_imp:
            val = getattr(morph, attr)
            if val[-4:] != "_any":
                variant_constraints += ((attr, val),)

    return variant_constraints


Corpora_to_pymorphy, Morph_to_db_id, Normal_to_db_id = {}, {}, {}


def from_pymorphy_labels_to_db_info(morph_cons_list, normal_form, prob):
    morph_db_id = Morph_to_db_id[morph_cons_list]
    normal_form_id = Normal_to_db_id[normal_form]
    return DBWordInfo(morph_db_id, normal_form_id, prob)


def from_corpora_to_db_info(word, normal_form, corpora_feat):
    pymorphy_labels = Corpora_to_pymorphy[(word, normal_form, corpora_feat)]
    return list(map(lambda lab: from_pymorphy_labels_to_db_info(*lab), pymorphy_labels))


if __name__ == '__main__':
    if "processed_file_index.pickle" not in os.listdir():  # храним первую необработанный
        text_index = 0
    else:
        with open('processed_file_index.pickle', 'rb') as tf:
            text_index = pickle.load(tf)
    pair_files = os.listdir("all")
    first_unproc_file_index = text_index
    try:  # TODO не убирать для нового файла !
        for file_ind in range(text_index, len(pair_files)):
            file_title = pair_files[file_ind]
            print(file_title)
            pair_list = get_pairs('all/' + file_title) # получаем список пар слов (не все из них - модели)
            text_corpora_labels = set()
            for (mw, mn, mm, dw, dn, dm, _, _) in pair_list:
                text_corpora_labels.add((mw, mn, mm))
                text_corpora_labels.add((dw, dn, dm))
            new_corpora_labels = {word_info: get_parse_by_pymorphy(*word_info)
                                  for word_info in text_corpora_labels - Corpora_to_pymorphy.items()}
            Corpora_to_pymorphy.update(new_corpora_labels)
            morph_constrations = set()
            normal_forms = set()
            for (m, nf, prob) in [e for lst in Corpora_to_pymorphy.values() for e in lst]:
                morph_constrations.add(m)
                normal_forms.add(nf)
            print("Corpora_to_pymorphy dict end")
            cursor = con.cursor()
            Morph_to_db_id.update({cons_lst: find_or_insert_morph_constraints(cons_lst, con, cursor)
                                   for cons_lst in morph_constrations - Morph_to_db_id.items()})
            print("Morph_to_db_id end")
            Normal_to_db_id.update({nf: find_or_insert_word(nf, con, cursor)
                                    for nf in normal_forms - Normal_to_db_id.items()})
            print("Normal_to_db_id end")
            i = 0
            pair_len = len(pair_list)
            for (mw, mn, mm, dw, dn, dm, _, _) in pair_list:
                insert_all_pairs(con, cursor, from_corpora_to_db_info(mw, mn, mm), from_corpora_to_db_info(dw, dn, dm))
                if i % 100 == 0:
                    print(i, pair_len, sep=" / ")
                i += 1
            print("not gp:", Counter, "/", pair_len )
            Counter = 0
            cursor.close()
        first_unproc_file_index += 1
    except Exception as exc:
        print(exc)
        with open('processed_file_index.pickle', 'wb') as f:
            pickle.dump(first_unproc_file_index, f)