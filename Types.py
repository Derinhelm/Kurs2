
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



NUMBER_PARAMETRS = 13

class Morf: # для хранения морфологических характеристик
    names = set(['s_cl', 'animate', 'gender', 'number', 'case_morph', 'reflection', 'perfective',\
            'transitive', 'person', 'tense', 'voice', 'degree', 'static'])
    def __init__(self, cl  = 'not_imp', an = 'not_imp', \
                 gen = 'not_imp', num = 'not_imp', \
                 cas = 'not_imp', ref = 'not_imp',\
                 perf = 'not_imp', trans = 'not_imp',\
                 pers = 'not_imp', ten = 'not_imp',\
                v = 'not_imp', deg = 'not_imp', stat = 'not_imp'):
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
    def __eq__(self, other):
        if isinstance(other, Morf):
            return self.s_cl == other.s_cl and self.animate == other.animate and self.gender == other.gender and self.number == other.number and \
                self.case_morph == other.case_morph and self.reflection == other.reflection and self.perfective == other.perfective and self.transitive == other.transitive and \
                self.person == other.person and self.tense == other.tense and self.voice == other.voice and self.degree == other.degree and self.static == other.static
        return NotImplemented
    
    