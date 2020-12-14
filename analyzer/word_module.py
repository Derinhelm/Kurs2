import pymorphy2

from analyzer.constants import *
from analyzer.functions import get_patterns


class Morph:  # для хранения морфологических характеристик
    names = ['s_cl', 'animate', 'gender', 'number', 'case_morph', 'reflection', 'perfective',
             'transitive', 'person', 'tense', 'voice', 'degree', 'static', 'prep_type']

    @staticmethod
    def create_s_cl(cur_parse):
        if cur_parse.normal_form == "себя":
            return 'reflexivepronoun'
        elif cur_parse.normal_form in ['я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они']:
            return 'personalpronoun'
        elif 'Apro' in cur_parse.tag:
            if str(cur_parse.tag.POS) == 'ADJF':
                return 'pronounadjective'
        elif 'Impe' in cur_parse.tag:
            return 'unpersonalverb'
        elif 'Mult' in cur_parse.tag:
            return 'frequentativeverb'
        elif 'Anum' in cur_parse.tag:
            return 'numberordinal'  # проверить!!!!
        elif cur_parse.normal_form == "один":
            return 'numberone'
        elif cur_parse.normal_form in ['два', 'оба', 'полтора']:
            return 'numbertwo'
        elif cur_parse.normal_form in ['три', 'четыре', 'сколько', 'несколько', 'столько', 'много',
                                       'немного'] or 'Coll' in cur_parse.tag:
            return 'numberthree'
        else:
            return cl[str(cur_parse.tag.POS)]

    @staticmethod
    def create_gender(cur_parse):
        if "Ms-f" in cur_parse.tag:
            return 'malefemale'
        else:
            return gend[str(cur_parse.tag.gender)]

    @staticmethod
    def create_reflection(cur_parse, text):
        # if 'Refl' in self.tag:
        #    self.Reflection = Ereflection.reflexive
        # как сделать reflexiveForm ??
        cur_cl = cur_parse.tag.POS
        if cur_cl in ('VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'PRED'):  # PRED -кат.сост. мб убрать
            if text[-2:] == "ся":
                if cur_cl == 'VERB' or cur_cl == 'INFN':
                    return 'reflexive'
                else:
                    return 'reflexive_form'
            else:
                return 'unreflexive'
        else:
            return 'reflection_any'

    @staticmethod
    def create_tense(cur_parse):
        cur_cl = cur_parse.tag.POS
        if cur_cl == 'INFN':
            return 'infinitive'
        elif cur_parse.tag.mood == 'impr':
            return 'imperative'
        else:
            return tense[str(cur_parse.tag.tense)]

    def create_static(self, cur_parse):
        if len(
                cur_parse.lexeme) == 1 or self.s_cl == 'preposition' or self.s_cl == 'gerund' \
                or self.s_cl == 'conjunction' or self.s_cl == 'interjection' or self.s_cl == 'adverb':
            return 'true'
        else:
            return 'false'

    def create_prep_type(self, text):
        if self.s_cl == 'preposition':
            if text in prep_type_dict.keys():
                self.prep_type = prep_type_dict[text]
                # toDo если новый предлог, для него надо искать тип(как-то писать в логи)
                return
        return "prep_type_any"

    def __init__(self, cur_parse, text):
        self.s_cl = self.create_s_cl(cur_parse)
        self.animate = anim[str(cur_parse.tag.animacy)]
        self.gender = self.create_gender(cur_parse)
        self.number = numb[str(cur_parse.tag.number)]
        self.case_morph = cas[str(cur_parse.tag.case)]
        self.reflection = self.create_reflection(cur_parse, text)
        self.perfective = perf[str(cur_parse.tag.aspect)]
        self.transitive = trans[str(cur_parse.tag.transitivity)]
        self.person = pers[str(cur_parse.tag.person)]
        self.tense = self.create_tense(cur_parse)
        self.voice = voice[str(cur_parse.tag.voice)]
        self.degree = 'degree_any'  # toDo научиться выделять
        self.static = self.create_static(cur_parse)
        self.prep_type = self.create_prep_type(text)

    def __setattr__(self, attr, value):  # Morph - неизменяемый класс
        if attr not in self.__dict__.keys():
            self.__dict__[attr] = value  # разрешаем редактировать только один раз
        return

    def __repr__(self):
        s = ""
        for curName in self.names:
            value = getattr(self, curName)
            if value.count("_any") == 0 and value != 'false':
                s += value + "; "
        return s

    def __eq__(self, other):
        if isinstance(other, Morph):
            return \
                self.s_cl == other.s_cl and self.animate == other.animate and self.gender == other.gender \
                and self.number == other.number and self.case_morph == other.case_morph and \
                self.reflection == other.reflection and self.perfective == other.perfective and \
                self.transitive == other.transitive and self.person == other.person and \
                self.tense == other.tense and self.voice == other.voice and self.degree == other.degree \
                and self.static == other.static
        return NotImplemented

    def get_imp(self):  # toDo что-то с _any ? В базе не будет требований _any, значит, поля неважны!
        imp_list = []
        for cur_name in self.names:
            value = getattr(self, cur_name)
            imp_list.append(value)
        return imp_list

    def check_imp(self, check_list):
        for cur_param in check_list:
            if getattr(self, dict_field[cur_param]) != cur_param:
                return False
        return True

    def is_preposition(self):
        return self.s_cl == 'preposition'

    def is_verb(self):
        return self.s_cl == 'verb'

    def is_noun_or_adj(self):
        return self.s_cl in ['noun', 'adjective', 'participle']

    def is_nominative(self):
        return self.case_morph == 'nominative'

    def get_homogeneous_params(self):
        return (self.s_cl, self.case_morph, self.prep_type)

class WordForm:
    def __init__(self, morph: Morph, normal_form, prob):
        self.normal_form = normal_form
        self.morph: Morph = morph
        self.g_patterns = []  # список из Gpattern, в которых данная словоформа мб главной
        self.probability = prob  # вероятность разбора из pymorphy2

    def __repr__(self):
        return self.normal_form + " " + self.morph.__repr__()

    def create_patterns(self, con):
        cursor = con.cursor()
        morph_constr = self.morph.get_imp()
        cur_first = get_patterns(cursor, 1, main_morph_params=morph_constr)
        cur_sec = get_patterns(cursor, 2, main_morph_params=morph_constr, main_word_param=self.normal_form)
        cur_third = get_patterns(cursor, 3, main_morph_params=morph_constr, main_word_param=self.normal_form)
        cursor.close()
        self.g_patterns += cur_third
        self.g_patterns += cur_sec
        self.g_patterns += cur_first
        print(len(self.g_patterns))
        return

    def get_patterns(self):
        return self.g_patterns


class Word:
    def __init__(self, con, morph_analyzer: pymorphy2.MorphAnalyzer, word_text):
        self.word_text = word_text
        self.forms = []
        self.morph_parse(con, morph_analyzer)

    def morph_parse(self, con, morph_analyzer: pymorphy2.MorphAnalyzer):
        if self.word_text[-1] == '.':
            p = morph_analyzer.parse(self.word_text[:-1])
            abbr = True
        else:
            p = morph_analyzer.parse(self.word_text)
            abbr = False
        for cur_parse in p:
            if (abbr and 'Abbr' in cur_parse.tag) or \
                    (not abbr and 'Abbr' not in cur_parse.tag):
                # чтобы предлогу "к" не приписывался вариант кандидат
                morph = Morph(cur_parse, self.word_text)
                cur_form = WordForm(morph, cur_parse.normal_form, cur_parse.score)
                cur_form.create_patterns(con)
                self.forms.append(cur_form)
        return

    def get_all_form_patterns(self):
        return [form.g_patterns for form in self.forms]

    def first_conj_variant(self):
        '''Возвращает индекс первого союзного варианта разбора, если нет, то None'''
        return next((ind for (ind, x) in enumerate(self.forms) if x.morph.s_cl == 'conjunction'), None)