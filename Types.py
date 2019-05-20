import postgresql
from enum import Enum
db = postgresql.open('pq://derin:qwerty@localhost:5432/models')
Es_cl = Enum('Es_cl','noun personalpronoun reflexivepronoun pronoun \
    name adjective possesiveadjective pronounadjective numberordinal\
    participle shortadjective shortparticiple comparative verb \
    unpersonalverb frequentativeverb gerund numberone numbertwo \
    numberthree number numberbiform adverb preposition conjunction \
    predicative particle interjection acronym S_clAny')
Eanimate = Enum('Eanimate', 'animate unanimate animateAny')
Egender = Enum('Egender', 'male female neuter malefemale maleorfemale genderAny')
Enumber = Enum('Enumber', 'single plural numberAny')
Ecase = Enum('Ecase', 'nominative genitive dative accusative\
    instrumental prepositional caseAny')
Ereflection = Enum('Ereflection', 'reflexive unreflexive \
    reflexiveForm reflectionAny')
Eperfective = Enum('Eperfective', 'perfective unperfective \
    perfectiveAny')
Etransitive = Enum('Etransitive', 'transitive untransitive transitiveAny')
Eperson = Enum('Eperson', 'first second third personAny')
Etense = Enum('Etense', 'infinitive present past future \
    imperative tenseAny')
Evoice = Enum('Evoice', 'active passive voiceAny')
Edegree = Enum('Edegree', 'strong weak degreeAny')
Enums = [Es_cl, Eanimate, Egender, Enumber, Ecase, Ereflection, Eperfective, Etransitive, \
        Eperson, Etense, Evoice, Edegree]

#словари соотвествия между нашими обозначениями и метками анализатора
cl = {'NOUN':Es_cl.noun, 'ADJF': Es_cl.adjective, 'ADJS': Es_cl.shortadjective, \
     'COMP':Es_cl.comparative, 'VERB': Es_cl.verb, 'INFN':Es_cl.verb, 'PRTF': Es_cl.participle,\
     'PRTS': Es_cl.shortparticiple, 'GRND':Es_cl.gerund, 'NUMR':Es_cl.number, \
     'ADVB': Es_cl.adverb, 'NPRO':Es_cl.pronoun, 'PRED': Es_cl.predicative, \
     'PREP': Es_cl.preposition, 'CONJ': Es_cl.conjunction, 'PRCL': Es_cl.particle, \
     'INTJ': Es_cl.interjection, 'None': Es_cl.S_clAny}
#есть в классификации, нет в pymorphy2
#personalpronoun reflexivepronoun name possesiveadjective pronounadjective numberordinal
#unpersonalverb frequentativeverb numberone numbertwo numberthree numberbiform
#parenthesis acronym S_clAny
anim = {'anim':Eanimate.animate, 'inan':Eanimate.unanimate, 'None':Eanimate.animateAny}
gend = {'masc':Egender.male, 'femn':Egender.female, 'neut':Egender.neuter, 
            'ms-f':Egender.malefemale, 'None':Egender.genderAny}#нет maleorfemale
#Ms-f не является значением p.tag.gender
numb = {'sing': Enumber.single, 'plur': Enumber.plural, 'None': Enumber.numberAny}
#нет Sgtm singularia tantum
#Pltm pluralia tantum
#Fixd неизменяемое !!!!!
cas = {'nomn':Ecase.nominative, 'gent':Ecase.genitive, 'datv':Ecase.dative, \
           'accs': Ecase.accusative, 'ablt': Ecase.instrumental, 'loct': Ecase.prepositional,\
          'None': Ecase.caseAny}
#нет
#voct	зв	звательный падеж	nomn
#gen1	рд1	первый родительный падеж	gent
#gen2	рд2	второй родительный (частичный) падеж	gent
#acc2	вн2	второй винительный падеж	accs
#loc1	пр1	первый предложный падеж	loct
#loc2	пр2	второй предложный (местный) падеж	loct
perf = {'perf': Eperfective.perfective, 'impf': Eperfective.unperfective, \
            'None':Eperfective.perfectiveAny}
trans = {'tran':Etransitive.transitive, 'intr': Etransitive.untransitive,\
             'None':Etransitive.transitiveAny}
pers = {'1per': Eperson.first, '2per': Eperson.second, '3per': Eperson.third, \
           'None':Eperson.personAny}
tense = {'pres': Etense.present,'past':Etense.past, 'futr': Etense.future, \
        'None':Etense.tenseAny, 'inf': Etense.infinitive, 'imp':Etense.imperative}
voice = {'actv':Evoice.active, 'pssv': Evoice.passive, 'None':Evoice.voiceAny}

NUMBER_PARAMETRS = 13

columns_imp_feat = db.query("SELECT column_name FROM information_schema.columns WHERE table_name = 'important_features' AND table_schema = 'public';")

columns_morf = db.query("SELECT column_name FROM information_schema.columns WHERE table_name = 'morf_characters_of_word' AND table_schema = 'public';")

class Morf: # для хранения морфологических характеристик
    def __init__(self, cl  = Es_cl.S_clAny, an = Eanimate.animateAny, \
                 gen = Egender.genderAny, num = Enumber.numberAny, \
                 cas = Ecase.caseAny, ref = Ereflection.reflectionAny,\
                 perf = Eperfective.perfectiveAny, trans = Etransitive.transitiveAny,\
                 pers = Eperson.personAny, ten = Etense.tenseAny,\
                v = Evoice.voiceAny, deg = Edegree.degreeAny, stat = False):
        self.s_cl = cl
        self.animate = an
        self.gender = gen
        self.number = num
        self.case1 = cas
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
                self.case1 == other.case1 and self.reflection == other.reflection and self.perfective == other.perfective and self.transitive == other.transitive and \
                self.person == other.person and self.tense == other.tense and self.voice == other.voice and self.degree == other.degree and self.static == other.static
        return NotImplemented
EUsedPrep = Enum("EUsedPrep", "noPrep, usedPrep")
