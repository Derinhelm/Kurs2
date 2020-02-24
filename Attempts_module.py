import copy

def FindBestPatternInList(paramList):
    '''find the best pair main word + pattern, return number of this pair'''
    # paramList - вида [(номер главного слова, модель управления)]
    best_pattern_1_number, best_pattern_2_number, best_pattern_3_number = None, None, None
    mark_best_pattern_1, mark_best_pattern_2, mark_best_pattern_3 = -1, -1, -1
    for i in range(len(paramList)):
        curPattern = paramList[i][1]
        curMark = curPattern.mark
        curLevel = curPattern.level
        if curLevel == 1:
            if curMark > mark_best_pattern_1:
                mark_best_pattern_1 = curMark
                best_pattern_1_number = i
        elif curLevel == 2:
            if curMark > mark_best_pattern_2:
                mark_best_pattern_2 = curMark
                best_pattern_2_number = i
        else:
            if curMark > mark_best_pattern_3:
                mark_best_pattern_3 = curMark
                best_pattern_3_number = i
    if best_pattern_3_number != None:
        return best_pattern_3_number
    elif best_pattern_2_number != None:
        return best_pattern_2_number
    elif best_pattern_1_number != None:
        return best_pattern_1_number
    else:
        return None


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
        self.flagEnd = False
        if self.depWords != []:
            self.curDep = self.depWords[self.pointCurDep]
        else:
            self.curDep = None
            self.changeDirect()

    def next(self):
        self.pointCurDep += 1
        if self.pointCurDep != len(self.depWords):
            self.curDep = self.depWords[self.pointCurDep]
            return self.depWords[self.pointCurDep]
        return self.changeDirect()

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

    def deleteInCurHalf(self, deleteDepNumber):
        # меняем depWords, тк найденное зависимое слово было в depWords, а не в другом направлении
        print(self.pointCurDep, self.depWords)
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

    def deleteFromTwoPart(self, deleteDepNumber):
        leftPart = list(filter(lambda x: x[0] == deleteDepNumber, self.leftDepWords))
        if leftPart != []:
            # удаляемое в левой половине
            if self.depDirection == -1:
                # левая часть - текущая
                self.deleteInCurHalf(deleteDepNumber)
            else:
                self.leftDepWords = list(filter(lambda x: x[0] != deleteDepNumber, self.leftDepWords))
                return self.leftDepWords
        else:
            # удаляемое в правой половине
            if self.depDirection == 1:
                # правая - текущая
                self.deleteInCurHalf(deleteDepNumber)
            else:
                self.rightDepWords = list(filter(lambda x: x[0] != deleteDepNumber, self.rightDepWords))
                return self.rightDepWords

    def changeDirect(self):
        if not self.flagOtherDirection:
            # Смотрели только в одном направлении, смотрим в другом
            self.flagOtherDirection = True
            self.pointCurDep = 0
            self.depWords = self.leftDepWords
            self.depDirection *= -1
            if len(self.depWords) > 0:
                self.curDep = self.depWords[self.pointCurDep]
                return self.depWords[0]
        self.flagEnd = True
        return None


class Attempts:
    def __init__(self, mainWord, pattternsMainWord, dep, allPatternsListParam):
        self.allPatternsList = allPatternsListParam # для дальнешего извлечения моделей
        self.mainPatternList = [(mainWord, pattern) for pattern in pattternsMainWord]
        # список вида [(главное слово, модель управления)]
        self.dependentsList = dep
        self.currentMain = None
        self.currentPattern = None
        self.currentDep = None
        self.currendMainPatternIndex = None # индекс текущей пары главное + модель в mainPatternList
        self.depDict = {} # по главному + модели возвращается DepWords
        self.flagEnd = False

        self.next()

    def next(self):
        if self.flagEnd: # вообще использоваться не должно, но в точке, где уже нет моделей, следующей тоже нет
            print("Error!!!!")
            return
        if self.currentDep != None:
            newDep = self.currentDep.next()
            if newDep != None:
                return
        self.nextMainPattern()

    def nextMainPattern(self):
        # ищем пару (главное слово, модель) с максимальной оценкой(лучше 3 уровня, потом 2, потом 1)
        numberOfBestPair = FindBestPatternInList(self.mainPatternList)
        if numberOfBestPair == None:
            (self.currentMain, self.currentPattern, self.currentDep) = (None, None, None)
            return None
        if self.currentDep != None and self.currentDep.flagEnd != True: # сохраняем информацию о просмотренных пот.зависимых старого пот.главного
            oldKey = (self.currentMain, self.currentPattern)
            self.depDict[oldKey] = self.currentDep
        if self.currendMainPatternIndex != None:
            # удаляем пару (главное, модель) из списка и из словаря,
            # тк мы проверили для нее все зависимые, больше с ней ничего сделать нельзя
            self.mainPatternList.pop(self.currendMainPatternIndex)
        if (self.currentMain, self.currentPattern) in self.depDict.keys():
            self.depDict.pop((self.currentMain, self.currentPattern))
        (self.currentMain, self.currentPattern) = self.mainPatternList[numberOfBestPair]
        self.currendMainPatternIndex = numberOfBestPair
        self.getDepForNewPairMainPattern(self.currentMain, self.currentPattern)
        return (self.currentMain, self.currentPattern)

    def get(self):
        if self.flagEnd:
            return None
        return (self.currentMain, self.currentPattern, self.currentDep.curDep[0], self.currentDep.curDep[1])

    def apply(self):
        '''currentDep - фиксируем, переводим его в main, удаляем из Dep все с данным зависимым'''
        newParsed = self.currentDep.curDep[0]
        self.addNewMain(self.currentDep.curDep)
        deletedKeys = []
        for key in self.depDict.keys():
            delRes = self.depDict[key].deleteFromTwoPart(newParsed)
            # None возвращается, если запустили deleteInCurHalf, и она вернула None(те пот.зависимые закончились)
            # те для данной пары key = (главное, модель) в новой точке разбора нет зависимых, те ее надо удалить из словаря и из списка
            if delRes == None:
                deletedKeys.append(key)
                self.mainPatternList.remove(key)
        for delKey in deletedKeys:
            self.depDict.pop(delKey)
        self.dependentsList = list(filter(lambda x: x[0] != newParsed, self.dependentsList))
        delRes = self.currentDep.deleteInCurHalf(newParsed)
        if delRes == None:
            self.nextMainPattern()


    def addNewMain(self, newMain):
        curMain = newMain[0]
        curVariant = newMain[1]
        patternsNewMain = self.allPatternsList[curMain][curVariant]
        mainPatternsNewMain = [(curMain, pattern) for pattern in patternsNewMain]
        numberNewBestPair = FindBestPatternInList(mainPatternsNewMain)
        (bestNewMain, bestNewPattern) = mainPatternsNewMain[numberNewBestPair]
        if self.currentPattern < bestNewPattern:
            # среди новых моделей есть более вероятная, идем к ней
            self.depDict[(self.currentMain, self.currentPattern)] = self.currentDep
            (self.currentMain, self.currentPattern) = (bestNewMain, bestNewPattern)
            self.currendMainPatternIndex = numberNewBestPair
            self.currentDep = DepWords(self.dependentsList, curMain)
            # пара главное + модель - новая, в depDict ее нет
        self.mainPatternList += mainPatternsNewMain

    def getDepForNewPairMainPattern(self, newMain, newPattern):
        newKey = (newMain, newPattern)
        if newKey in self.depDict.keys():
            self.currentDep = self.depDict[newKey]
        else:
            self.currentDep = DepWords(self.dependentsList, newMain)