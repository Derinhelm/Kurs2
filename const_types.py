from constants import *

NUMBER_PARAMETRS = 14


class Morph:  # для хранения морфологических характеристик
    names = ['s_cl', 'animate', 'gender', 'number', 'case_morph', 'reflection', 'perfective',
             'transitive', 'person', 'tense', 'voice', 'degree', 'static', 'prep_type']

    @staticmethod
    def create_s_cl(cur_parse):
        if cur_parse.normal_form == "себя":
            return 'reflexivepronoun'
        elif cur_parse.normal_form in ['я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они']:
            return 'personalpronoun'
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
        self.probability = cur_parse.score  # вероятность разбора из pymorphy2
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
            if value.count("_any") == 0:
                s += value + ";"
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


class GPattern:
    def __init__(self, l, mw, dw, mark, mc, dc):
        self.level = l
        self.main_word = mw
        self.dependentWord = dw
        self.mark = mark
        self.main_wordConstraints = mc  # массив ограничений на морф
        self.dependentWordConstraints = dc  # массив ограничений на морф

    def __repr__(self):
        s = str(self.level) + ":"
        if self.level == 3:
            s += " " + self.dependentWord
        s += " " + str(self.mark) + " "
        for c in self.dependentWordConstraints:
            s += " " + c + ";"
        return s

    def __lt__(self, other):  # x < y
        if self.level < other.level:
            return True
        if self.level > other.level:
            return False
        return self.mark < other.mark

    def get_dep_morph_constraints(self):
        return self.dependentWordConstraints

    def get_dep_word(self):
        return self.dependentWord
