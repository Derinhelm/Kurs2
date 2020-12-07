import xml.dom.minidom
from constants import name_files
import pickle

# В этом файле мы ничего не делаем с морфологией (про нее ничего не знаем)! Мы работаем с ней только в fill.py
# Здесь работает с синтаксическим деревом

class WordFromCorpora:
    def __init__(self, word_id, dom_id, feat, word, normal_form, link_type):
        self.id = word_id
        self.dom_id = dom_id
        self.feat = feat
        self.word = word
        self.normal_form = normal_form
        self.link_type = link_type

    def __str__(self):
        return str(self.id) + self.word


def parse_xml(name_file):
    doc = xml.dom.minidom.parse(name_file)
    parsed_sentence_list = []
    parent = doc.getElementsByTagName('S')
    for item in parent:
        new_sentence = []
        child_parent_dict = {}  # ключ - родительская вершина, значение - список дочерних вершин (из СинТагРус)
        for child in item.getElementsByTagName('W'):  # слова с пробелами пока не учитываем
            (cur_id, feat, norm_word, link_type) = (int(child.getAttribute('ID')) - 1, child.getAttribute('FEAT'),
                                                    child.getAttribute('LEMMA'), child.getAttribute('LINK'))
            # делаем id - 1, dom_id - 1, тк в СинТагРус нумерация с 1, а не с 0
            dom = child.getAttribute('DOM')
            if dom == '_root':
                child_parent_dict["root"] = [cur_id]
                link_type = None  # главное слово, нет связи
                dom_id = None
            else:
                dom_id = int(dom) - 1
                if dom_id in child_parent_dict:
                    child_parent_dict[dom_id].append(cur_id)
                else:
                    child_parent_dict[dom_id] = [cur_id]
            if len(child.childNodes) != 0:
                word = child.childNodes[0].nodeValue.lower()
            else:
                word = None
            norm_word = norm_word.lower()
            new_word = WordFromCorpora(cur_id, dom_id, feat, word, norm_word, link_type)
            new_sentence.append(new_word)
        parsed_sentence_list.append((new_sentence, child_parent_dict))
    return parsed_sentence_list


def get_main_number(cur_word, dep_main_word_dict):
    if cur_word.link_type in ['сочин', 'соч-союзн']:
        # собирали_0 грибы_1 и_2 ягоды_3. Собирали_0 + грибы_1, грибы_1 + и_2, и_2 + ягоды_3;
        # dep_main_word_dict должен быть {1: 0, 2: 1, 3: 2}
        # хотим модели Собирали + грибы, собирали + ягоды
        cur_word.link_type = 'обраб.сочин'
        return dep_main_word_dict[cur_word.dom_id]

    return cur_word.dom_id


def is_gpattern(dep_word, main_word):
    '''Проверяет является ли пара слов моделью управления
    '''
    if dep_word.link_type in ['подч-союзн', 'инф-союзн', 'сравнит', 'сравн-союзн', 'сент-предик', 'релят', 'огранич',
                              'вводн', 'изъясн', 'разъяснит', 'примыкат', 'сент-соч', 'кратн',
                              'соотнос', 'эксплет']:
        return False
    if dep_word.link_type in ['сочин', 'соч-союзн']:
        raise TypeError
    return True


def insert(name_file, text_title):
    '''Вставка....
>>> print(1)
1

    '''
    cur_text_pair_list = []
    parsed_sentence_list = parse_xml(name_file)
    for sentence_number in range(len(parsed_sentence_list)):
        cur_sentence, child_parent_dict = parsed_sentence_list[sentence_number]
        dep_main_word_dict = {}  # ключ - номер зависимого слова, значение - номер главного слова
        root_id = child_parent_dict["root"][0]
        unvisited_words = [root_id]
        while unvisited_words != []:
            cur_id = unvisited_words.pop()
            if cur_id in child_parent_dict:
                unvisited_words += child_parent_dict[cur_id]  # добавляем дочерние слова для просмотра
            cur_word = cur_sentence[cur_id]
            main_word_number = get_main_number(cur_word, dep_main_word_dict)
            dep_main_word_dict[cur_id] = main_word_number
            if main_word_number is not None:  # если главное слово - не корень дерева
                # TODO Если несколько однородных сказуемых? Шли и бежали люди???
                # TODO если несколько одородных главных, но не сказуемых Красивые люди и быстрые собаки
                main_word = cur_sentence[main_word_number]
                if is_gpattern(cur_word, main_word):
                    new_pair = (main_word.word, main_word.normal_form, main_word.feat, cur_word.word,
                                cur_word.normal_form, cur_word.feat, text_title, sentence_number + 1)
                    cur_text_pair_list.append(new_pair)
    return cur_text_pair_list


'''file_name = 'tests/sochin.txt'
cur_pair_list = []
cur_pair_list = insert(file_name, file_name)
print(*cur_pair_list, sep="\n")
x = 0
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
        with open('pairs/' + text_title + '.pickle', 'wb') as f:
            pickle.dump(pairs_list, f)