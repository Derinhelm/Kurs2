
#словари соотвествия между нашими обозначениями и метками анализатора
cl = {'NOUN':'noun', 'ADJF': 'adjective', 'ADJS': 'shortadjective', \
     'COMP':'comparative', 'VERB': 'verb', 'INFN':'verb', 'PRTF': 'participle',\
     'PRTS': 'shortparticiple', 'GRND':'gerund', 'NUMR':'number', \
     'ADVB': 'adverb', 'NPRO':'pronoun', 'PRED': 'predicative', \
     'PREP': 'preposition', 'CONJ': 'conjunction', 'PRCL': 'particle', \
     'INTJ': 'interjection', 'None': 's_cl_any'}
#есть в классификации, нет в pymorphy2
#personalpronoun reflexivepronoun name possesiveadjective pronounadjective numberordinal
#unpersonalverb frequentativeverb numberone numbertwo numberthree numberbiform
#parenthesis acronym S_clAny
anim = {'anim':'animate', 'inan':'unanimate', 'None':'animate_any'}
gend = {'masc':'male', 'femn':'female', 'neut':'neuter', 
            'ms-f':'malefemale', 'None':'gender_any'}#нет maleorfemale
#Ms-f не является значением p.tag.gender
numb = {'sing': 'single', 'plur': 'plural', 'None': 'number_any'}
#нет Sgtm singularia tantum
#Pltm pluralia tantum
#Fixd неизменяемое !!!!!
cas = {'nomn':'nominative', 'gent':'genitive', 'datv':'dative', \
           'accs': 'accusative', 'ablt': 'instrumental', 'loct': 'prepositional',\
          'None': 'case_any', 'loc2': 'prepositional', 'gen2':'genitive'}

st = {True:'true', False:'false'}
#нет
#voct	зв	звательный падеж	nomn
#gen1	рд1	первый родительный падеж	gent
#gen2	рд2	второй родительный (частичный) падеж	gent
#acc2	вн2	второй винительный падеж	accs
#loc1	пр1	первый предложный падеж	loct
#loc2	пр2	второй предложный (местный) падеж	loct
perf = {'perf': 'perfective', 'impf': 'unperfective', \
            'None':'perfective_any'}
trans = {'tran':'transitive', 'intr': 'untransitive',\
             'None':'transitive_any'}
pers = {'1per': 'first', '2per': 'second', '3per': 'third', \
           'None':'person_any'}
tense = {'pres': 'present','past':'past', 'futr': 'future', \
        'None':'tense_any', 'inf': 'infinitive', 'imp':'imperative'}
voice = {'actv':'active', 'pssv': 'passive', 'None':'voice_any'}

dictField = {'noun':'s_cl', 'adjective':'s_cl', 'shortadjective':'s_cl', \
        'comparative':'s_cl', 'verb':'s_cl', 'verb':'s_cl', 'participle':'s_cl',\
        'shortparticiple':'s_cl', 'gerund':'s_cl', 'number':'s_cl', \
        'adverb':'s_cl', 'pronoun':'s_cl', 'personalpronoun':'s_cl', 'reflexivepronoun':'s_cl', 'predicative':'s_cl', \
        'preposition':'s_cl', 'conjunction':'s_cl', 'particle':'s_cl', \
        'interjection':'s_cl', 's_cl_any':'s_cl', \
        'animate':'animate', 'unanimate':'animate', 'animate_any':'animate', \
        'male':'gender', 'female':'gender', 'neuter':'gender', 'malefemale':'gender', 'gender_any':'gender', \
        'single':'number', 'plural':'number', 'number_any':'number', \
        'nominative':'case_morph', 'genitive':'case_morph', 'dative':'case_morph', \
        'accusative':'case_morph', 'instrumental':'case_morph', 'prepositional':'case_morph',\
        'case_any':'case_morph', 'prepositional':'case_morph', 'genitive':'case_morph', \
        'reflexive':'reflection', 'unreflexive':'reflection', 'reflexive_form':'reflection', 'reflection_any':'reflection', \
        'perfective':'perfective', 'unperfective':'perfective', 'perfective_any':'perfective', \
        'transitive':'transitive', 'untransitive':'transitive', 'transitive_any':'transitive', \
        'first':'person', 'second':'person', 'third':'person', 'person_any':'person', \
        'present':'tense','past':'tense', 'future':'tense', 'tense_any':'tense', \
        'infinitive':'tense', 'imperative':'tense', \
        'active':'voice', 'passive':'voice', 'voice_any':'voice', \
        'true':'static', 'false':'static', \
        'strong':'static', 'weak':'static', 'degree_any':'static',
        'a':'prep_type', 'dap':'prep_type', 'gai':'prep_type', \
        'ai':'prep_type', 'ap':'prep_type', 'd':'prep_type', \
        'gd':'prep_type', 'g':'prep_type', 'gi':'prep_type', \
        'i':'prep_type', 'p':'prep_type'
       }

NUMBER_PARAMETRS = 14
prepTypeDict = {'без': 'g',
 'безо': 'g',
 'благодаря': 'd',
 'близ': 'g',
 'в': 'ap',
 'вблизи': 'g',
 'ввиду': 'g',
 'вглубь': 'g',
 'вдоль': 'g',
 'взамен': 'g',
 'включая': 'a',
 'выключая': 'a',
 'вкось': 'g',
 'вкруг': 'g',
 'вместо': 'g',
 'вне': 'g',
 'внизу': 'g',
 'внутри': 'g',
 'внутрь': 'g',
 'во': 'ap',
 'вовнутрь': 'g',
 'возле': 'g',
 'вокруг': 'g',
 'вопреки': 'd',
 'вперед': 'g',
 'впереди': 'g',
 'вроде': 'g',
 'вослед': 'd',
 'вслед': 'd',
 'вследствие': 'g',
 'выше': 'g',
 'для': 'g',
 'до': 'g',
 'за': 'ai',
 'заместо': 'g',
 'из': 'g',
 'изо': 'g',
 'из-за': 'g',
 'из-под': 'g',
 'изнутри': 'g',
 'исключая': 'a',
 'к': 'd',
 'ко': 'd',
 'касаемо': 'g',
 'касательно': 'g',
 'кроме': 'g',
 'кругом': 'g',
 'меж': 'gi',
 'между': 'gi',
 'мимо': 'g',
 'минус': 'a',
 'на': 'ap',
 'наверху': 'g',
 'над': 'i',
 'надо': 'i',
 'навстречу': 'd',
 'наискось': 'g',
 'накануне': 'g',
 'наместо': 'g',
 'наперекор': 'd',
 'наперерез': 'd',
 'наподобие': 'g',
 'напротив': 'g',
 'насупротив': 'g',
 'насчет': 'g',
 'ниже': 'g',
 'о': 'ap',
 'об': 'ap',
 'обо': 'ap',
 'обок': 'g',
 'около': 'g',
 'окрест': 'g',
 'окромя': 'g',
 'округ': 'g',
 'опричь': 'g',
 'относительно': 'g',
 'от': 'g',
 'ото': 'g',
 'перед': 'i',
 'передо': 'i',
 'плюс': 'a',
 'пред': 'i',
 'предо': 'i',
 'по': 'dap',
 'по-за': 'a',
 'по-над': 'i',
 'поверх': 'g',
 'под': 'ai',
 'подле': 'g',
 'подо': 'ai',
 'подобно': 'd',
 'позади': 'g',
 'позадь': 'g',
 'помимо': 'g',
 'поперек': 'g',
 'посереди': 'g',
 'посередине': 'g',
 'посередь': 'g',
 'после': 'g',
 'посреди': 'g',
 'посредине': 'g',
 'посредством': 'g',
 'превыше': 'g',
 'прежде': 'g',
 'при': 'p',
 'про': 'a',
 'промеж': 'g',
 'промежду': 'g',
 'против': 'g',
 'противно': 'g',
 'путем': 'g',
 'ради': 'g',
 'с': 'gai',
 'со': 'gai',
 'сбоку': 'g',
 'сверх': 'g',
 'сверху': 'g',
 'свыше': 'g',
 'середь': 'g',
 'сзади': 'g',
 'сквозь': 'a',
 'снизу': 'g',
 'согласно': 'd',
 'сообразно': 'd',
 'соответственно': 'd',
 'соразмерно': 'd',
 'спереди': 'g',
 'спустя': 'a',
 'среди': 'g',
 'средь': 'g',
 'сродни': 'd',
 'супротив': 'g',
 'у': 'g',
 'через': 'a',
 'чрез': 'a',
 'без ведома': 'g',
 'близко от': 'g',
 'вблизи от': 'g',
 'в виде': 'g',
 'вдали от': 'g',
 'вдоль по': 'd',
 'в зависимости от': 'g',
 'в знак': 'g',
 'в качестве': 'g',
 'в кругу': 'g',
 'в лице': 'g',
 'в меру': 'g',
 'в направлении к': 'd',
 'во благо': 'gd',
 'во избежание': 'g',
 'во имя': 'g',
 'вместе с': 'i',
 'в ответ на': 'a',
 'в отличие от': 'g',
 'в отношении': 'g',
 'в отношении к': 'd',
 'в пандан': 'gd',
 'в преддверии': 'g',
 'в продолжение': 'g',
 'в противовес': 'd',
 'впредь до': 'g',
 'в результате': 'g',
 'в роли': 'g',
 'в связи с': 'i',
 'в силу': 'g',
 'в соответствии с': 'i',
 'вслед за': 'i',
 'в сравнении с': 'i',
 'в сторону от': 'g',
 'в течение': 'g',
 'в целях': 'g',
 'в центре': 'g',
 'в честь': 'g',
 'за вычетом': 'g',
 'за исключением': 'g',
 'за счет': 'g',
 'исходя из': 'g',
 'лицом к': 'd',
 'лицом к лицу с': 'i',
 'на благо': 'gd',
 'на виду у': 'g',
 'на глазах у': 'g',
 'на предмет': 'g',
 'на протяжении': 'g',
 'наравне с': 'i',
 'наряду с': 'i',
 'начиная с': 'g',
 'не без': 'g',
 'не говоря о': 'p',
 'незадолго до': 'g',
 'не считая': 'g',
 'недалеко от': 'g',
 'независимо от': 'g',
 'невзирая на': 'a',
 'несмотря на': 'a',
 'одновременно с': 'i',
 'от лица': 'g',
 'от имени': 'g',
 'по вопросу о': 'p',
 'по линии': 'g',
 'по мере': 'g',
 'по направлению к': 'd',
 'по отношению к': 'd',
 'по поводу': 'g',
 'по причине': 'g',
 'по пути к': 'd',
 'по случаю': 'g',
 'по сравнению с': 'i',
 'по части': 'g',
 'поблизости от': 'g',
 'под видом': 'g',
 'под эгидой': 'g',
 'применительно к': 'd',
 'при помощи': 'g',
 'рядом с': 'i',
 'с ведома': 'g',
 'следом за': 'i',
 'смотря по': 'd',
 'согласно с': 'i',
 'с помощью': 'g',
 'с прицелом на': 'a',
 'с течением': 'g',
 'судя по': 'd',
 'с точки зрения': 'g',
 'с целью': 'g'}

prepTypeToCaseDict = {
'a': ['accusative'],
'dap': ['dative', 'accusative', 'prepositional'],
'gai': ['genitive', 'accusative', 'instrumental'],
'ai': ['accusative', 'instrumental'],
'ap': ['accusative', 'prepositional'],
'd': ['dative'],
'gd': ['genitive', 'dative'],
'g': ['genitive'],
'gi': ['genitive', 'instrumental'],
'i': ['instrumental'],
'p': ['prepositional']
}
class Morph: # для хранения морфологических характеристик
    names = ['s_cl', 'animate', 'gender', 'number', 'case_morph', 'reflection', 'perfective',\
            'transitive', 'person', 'tense', 'voice', 'degree', 'static', 'prep_type']

    def __init__(self, prob = 0, cl  = 'not_imp', an = 'not_imp', \
                 gen = 'not_imp', num = 'not_imp', \
                 cas = 'not_imp', ref = 'not_imp',\
                 perf = 'not_imp', trans = 'not_imp',\
                 pers = 'not_imp', ten = 'not_imp',\
                v = 'not_imp', deg = 'not_imp', stat = 'not_imp', pt = 'not_imp'):
        self.s_cl = cl
        self.animate = an
        self.gender = gen
        self.number = num
        self.case_morph = cas
        self.reflection = ref
        self.perfective = perf
        self.transitive = trans
        self.person = pers
        self.tense = ten
        self.voice = v
        self.degree = deg
        self.static = stat
        self.probability = prob # из pymorphy2
        self.prep_type = pt

    def __repr__(self):
        s = ""
        for curName in self.names:
            value = getattr(self, curName)
            if value != 'not_imp' and value.count("_any") == 0:
                s += value + ","
        return s

    def __eq__(self, other):
        if isinstance(other, Morph):
            return self.s_cl == other.s_cl and self.animate == other.animate and self.gender == other.gender and self.number == other.number and \
                self.case_morph == other.case_morph and self.reflection == other.reflection and self.perfective == other.perfective and self.transitive == other.transitive and \
                self.person == other.person and self.tense == other.tense and self.voice == other.voice and self.degree == other.degree and self.static == other.static
        return NotImplemented

    def get_imp(self):
        imp_list = []
        for cur_name in self.names:
            value = getattr(self, cur_name)
            if value != 'not_imp':
                imp_list.append(value)
        return imp_list

    def check_imp(self, check_list):
        for cur_param in check_list:
            if getattr(self, dictField[cur_param]) != cur_param:
                return False
        return True

class GPattern:
    def __init__(self, l, mw, dw, mark, mc, dc):
        self.level = l
        self.mainWord = mw
        self.dependentWord = dw
        self.mark = mark
        self.mainWordConstraints = mc  # массив ограничений на морф
        self.dependentWordConstraints = dc  # массив ограничений на морф

    def __repr__(self):
        s = str(self.level) + ":"
        if self.level == 3:
            s += " " + self.dependentWord
        s += " " + str(self.mark) + " "
        for c in self.dependentWordConstraints:
            s += " " + c + ";"
        return s

    def __lt__(self, other): # x < y
        if self.level < other.level:
            return True
        if self.level > other.level:
            return False
        return self.mark < other.mark

    def get_dep_morph_constraints(self):
        return self.dependentWordConstraints

    def get_dep_word(self):
        return self.dependentWord