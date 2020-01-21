from bisect import bisect

class MainWords:
    def __init__(self, mw):
        self.pointCurMain = 0
        self.mainWords = mw # номера потенциальных главных слов
        self.curMain = self.mainWords[self.pointCurMain]# номер тек.главного

    def next(self):
        self.pointCurMain += 1
        if self.pointCurMain == len(self.mainWords):
            return None
        self.curMain = self.mainWords[self.pointCurMain]
        return self.curMain

class Patterns:
    def __init__(self, p):
        self.patterns = p
        self.pointCurPatt = 0
        self.curPatt = self.patterns[self.pointCurPatt]

    def next(self):
        self.pointCurPatt += 1
        if self.pointCurPatt == len(self.patterns):
            return None
        self.curPatt = self.patterns[self.pointCurPatt]
        return self.curPatt

class DepWords:
    def __init__(self, dep, curMain):
        bord = bisect(dep, curMain) # ищем, границу между левыми и правыми неразобранными
        self.leftDepWords = dep[:bord:-1]
        self.rightDepWords = dep[bord:]
        self.depDirection = 1  # 1 - вправо, -1 - влево
        self.depWords = self.rightDepWords  # потом будет leftDepWords
        self.flagOtherDirection = False
        self.pointCurDep = 0
        self.curDep = self.depWords[self.pointCurDep]

    def next(self):
        self.pointCurDep += 1
        if self.pointCurDep == len(self.depWords):
            return self.depWords[self.pointCurDep]
        if not self.flagOtherDirection:
            # Смотрели только в одном направлении, смотрим в другом
            self.flagOtherDirection = True
            self.pointCurDep = 0
            self.depWords = self.leftDepWords
            return self.depWords[0]
        return None

    def reset(self):
        '''Возвращаем указатели текущего зависимого и тп на начальные,
        используется при установке новой модели управления'''
        self.depDirection = 1
        self.depWords = self.rightDepWords  # потом будет leftDepWords
        self.flagOtherDirection = False
        self.pointCurDep = 0
        self.curDep = self.depWords[self.pointCurDep]

class Attempts:
    def __init__(self, mw, pat, dep):
        self.main = MainWords(mw)
        self.patterns = Patterns(pat)# модели управления для self.curMain
        self.dep = DepWords(dep, self.main.curMain)


    def next(self):
        newDep = self.dep.next()
        if newDep != None:
            return (self.main.curMain, self.patterns.curPatt, newDep)
        newPattern = self.patterns.next()
        if newPattern != None:
            self.dep.reset()
            return (self.main.curMain, newPattern, self.dep.curDep)
        newMain = self.main.next()
        if newMain != None:
            # загрузить новые модели
            self.dep.next()
        return None
