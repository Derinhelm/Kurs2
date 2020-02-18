import copy

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

    def getPattern(self):
        return self.curPatt

class MainWords:
    def __init__(self, mw, pats, allPatternsListParam):
        # pats - модели управления данного варианта данного слова
        self.pointCurMain = 0
        extMainWordsList = []
        for curMainVariant in mw:
            curPatterns = Patterns(pats)
            extMainWordsList.append((curMainVariant[0], curMainVariant[1], curPatterns))
        self.mainWords = extMainWordsList # номера потенциальных главных слов
        # список вида [(номер разобранного слова, номер варианта разбора этого слова, Patterns для данного варианта разбора слова)]
        self.curMain = self.mainWords[self.pointCurMain]# номер тек.главного
        self.allPatternsList = allPatternsListParam

    def add(self, newMain):
        curMain = newMain[0]
        curVariant = newMain[1]
        patternsNewMain = Patterns(self.allPatternsList[curMain][curVariant])
        extMainVariant = (curMain, curVariant, patternsNewMain)

        #Здесь можно менять, в какое место будет вставлено новое главное
        # продолжаем разбор с нового разобранного
        self.mainWords.insert(self.pointCurMain, extMainVariant)
        self.curMain = self.mainWords[self.pointCurMain]

        # новое - в конец
        #self.mainWords.append(extMainVariant)


    def nextMain(self):
        self.pointCurMain += 1
        if self.pointCurMain == len(self.mainWords):
            return None
        self.curMain = self.mainWords[self.pointCurMain]
        return self.curMain

    def nextPatternOrMain(self):
        newPattern = self.curMain[2].next() # обращаемся к Patterns текущего варианта разбора главного слова
        if newPattern != None:
            return newPattern
        newMain = self.nextMain()
        if newMain != None:
            return newMain
        return None

    def getPattern(self):
        return self.curMain[2].getPattern()

    def getMain(self):
        return self.curMain[0]

    def getMainVariant(self):
        return self.curMain[1]
class DepWords:
    def __init__(self, dep, curMain):
        self.leftDepWords = copy.deepcopy(dep)
        self.leftDepWords = list(filter(lambda x: x[0] < curMain, self.leftDepWords))
        self.rightDepWords = copy.deepcopy(dep)
        self.rightDepWords = list(filter(lambda x: x[0] > curMain, self.rightDepWords))
        self.depDirection = 1  # 1 - вправо, -1 - влево
        self.depWords = self.rightDepWords  # потом будет leftDepWords
        self.flagOtherDirection = False
        self.pointCurDep = 0
        self.curDep = self.depWords[self.pointCurDep]

    def next(self):
        self.pointCurDep += 1
        if self.pointCurDep != len(self.depWords):
            self.curDep = self.depWords[self.pointCurDep]
            return self.depWords[self.pointCurDep]
        return self.changeDirect()

    def reset(self):
        '''Возвращаем указатели текущего зависимого и тп на начальные,
        используется при установке новой модели управления'''
        self.depDirection = 1
        self.depWords = self.rightDepWords  # потом будет leftDepWords
        self.flagOtherDirection = False
        self.pointCurDep = 0
        if self.pointCurDep == len(self.depWords):
            res = self.changeDirect()
            if res == None:
                print("Случилось невозможное") # Тк мы попали в reset, то зависимые есть, но здесь правые и левые зависимые - []
        else:
            self.curDep = self.depWords[self.pointCurDep]

    def changeDepList(self, newDep):
        if self.depDirection == 1:
            self.rightDepWords = newDep
            self.depWords = self.rightDepWords
        else:
            self.leftDepWords = newDep
            self.depWords = self.leftDepWords

    def deleteNumberFromDepList(self, deleteDepNumber):
        newDep = list(filter(lambda x: x[0] != deleteDepNumber, self.depWords))
        self.changeDepList(newDep)

    def delete(self, deleteDepNumber):
        # меняем depWords, тк найденное зависимое слово было в depWords, а не в другом направлении
        while self.pointCurDep != len(self.depWords) and self.depWords[self.pointCurDep][0] == deleteDepNumber:
            self.pointCurDep += 1
        if self.pointCurDep == len(self.depWords):
            self.deleteNumberFromDepList(deleteDepNumber)
            return None
        oldLen = len(self.depWords)
        self.deleteNumberFromDepList(deleteDepNumber)
        countDel = oldLen - len(self.depWords)
        self.pointCurDep -= countDel
        self.curDep = self.depWords[self.pointCurDep]
        return self.curDep


        # указатель текущего зависимого надо поставить на следующее в depWords значение, у которого первое поле != удаляемому
    # варианты 1. deleteDepNumber = 2 [(1, 0), (1, 1), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1)],
    # результат [(1, 0), (1, 1), (3, 0), (3, 1)] curDep = (3, 0)
    # 2. deleteDepNumber = 2 [(1, 0), (1, 1), (2, 0), (2, 1), (2, 2)],
    # результат [(1, 0), (1, 1)], и надо менять направление
    # если нельзя поменять направление, то переходим к следующей модели(или к следующему главному)

    def changeDirect(self):
        if not self.flagOtherDirection:
            # Смотрели только в одном направлении, смотрим в другом
            self.flagOtherDirection = True
            self.pointCurDep = 0
            self.depWords = self.leftDepWords
            if len(self.depWords) > 0:
                self.curDep = self.depWords[self.pointCurDep]
                return self.depWords[0]
        return None


class Attempts:
    def __init__(self, mw, patsForMain, dep, allPatternsListParam):
        self.main = MainWords(mw, patsForMain, allPatternsListParam)
        self.dep = DepWords(dep, self.main.curMain[0])
        self.flagEnd = False

    def next(self):
        if self.flagEnd: # вообще использоваться не должно, но в точке, где уже нет моделей, следующей тоже нет
            print("Error!!!!")
            return
        newDep = self.dep.next()
        if newDep != None:
            return
        res = self.main.nextPatternOrMain()
        if res != None:
            self.dep.reset()
        else:
            self.flagEnd = True

    def get(self):
        if self.flagEnd:
            return None
        return (self.main.getMain(), self.main.getPattern(), self.dep.curDep[0], self.dep.curDep[1])

    def apply(self):
        '''curDep - фиксируем, переводим его в main, удаляем из Dep все с данным зависимым'''
        self.main.add(self.dep.curDep)
        resDel = self.dep.delete(self.dep.curDep[0])
        if resDel == None:
            if self.dep.leftDepWords == [] and self.dep.rightDepWords == []:
                self.flagEnd = True
                return
            resChangeDirect = self.dep.changeDirect()
            if resChangeDirect == None:
                # не вышло поменять направление - надо менять модель или главное
                res = self.main.nextPatternOrMain()
                if res != None:
                    self.dep.reset()
                else:
                    self.flagEnd = True