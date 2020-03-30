import copy
f =open("writeList", "w")
f1 =open("writeList-trass", "w")
SIMILAR_PARAM = 450

def FindBestPatternInList(paramList):
    '''find the best pair main word + pattern, return number of this pair'''
    # paramList - вида [(номер главного слова, модель управления)]
    best_pattern_1_number, best_pattern_2_number, best_pattern_3_number = None, None, None
    mark_best_pattern_1, mark_best_pattern_2, mark_best_pattern_3 = -1, -1, -1
    for i in range(len(paramList)):
        curPattern = paramList[i][1]
        f1.write(str(paramList[i][0]) + "       "+ curPattern.__repr__())
        f1.write("\n")
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
    if best_pattern_3_number:
        f.write("3:" + str(mark_best_pattern_3) + str(paramList[best_pattern_3_number]))
        f.write("\n")
    if best_pattern_2_number:
        f.write("2:" + str(mark_best_pattern_2) + str(paramList[best_pattern_2_number]))
        f.write("\n")
    if best_pattern_1_number:
        f.write("1:" + str(mark_best_pattern_1) + str(paramList[best_pattern_1_number]))
        f.write("\n")
    f.write("------------------------------------------------")
    f.write("\n")
    f1.write("------------------------------------------------")
    f1.write("\n")

    if mark_best_pattern_1 != -1:
        if mark_best_pattern_2 != -1:
            if mark_best_pattern_3 != -1:
                # 1+, 2+, 3+
                if mark_best_pattern_2 - mark_best_pattern_3 > SIMILAR_PARAM:
                    if mark_best_pattern_1 - mark_best_pattern_2 > SIMILAR_PARAM:
                        return best_pattern_1_number
                    else:
                        return best_pattern_2_number
                else:
                    if mark_best_pattern_1 - mark_best_pattern_3 > SIMILAR_PARAM:
                        return best_pattern_1_number
                    else:
                        return best_pattern_3_number
            else:
                # 1+, 2+, 3-
                if mark_best_pattern_1 - mark_best_pattern_2 > SIMILAR_PARAM:
                    return best_pattern_1_number
                else:
                    return best_pattern_2_number
        else:
            if mark_best_pattern_3 != -1:
                # 1+, 2-, 3+
                if mark_best_pattern_1 - mark_best_pattern_3 > SIMILAR_PARAM:
                    return best_pattern_1_number
                else:
                    return best_pattern_3_number
            else:
                # 1+, 2-, 3-
                return best_pattern_1_number
    else:
        if mark_best_pattern_2 != -1:
            if mark_best_pattern_3 != -1:
                # 1-, 2+, 3+
                if mark_best_pattern_2 - mark_best_pattern_3 > SIMILAR_PARAM:
                    return best_pattern_2_number
                else:
                    return best_pattern_3_number
            else:
                # 1-, 2+, 3-
                return best_pattern_2_number
        else:
            if mark_best_pattern_3 != -1:
                # 1-, 2-, 3+
                return best_pattern_3_number
            else:
                # 1-, 2-, 3-
                return None

    #if best_pattern_3_number != None:
    #    return best_pattern_3_number
    #elif best_pattern_2_number != None:
        #if mark_best_pattern_2 >
    #    return best_pattern_2_number
    #elif best_pattern_1_number != None:
    #    return best_pattern_1_number
    #else:
    #    return None

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
        #print(self.pointCurDep, self.depWords)
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
    def __init__(self, main_word_index, pattternsMainWord, dep, allPatternsListParam, morphPosition, wordPosition):
        self.allPatternsList = allPatternsListParam # для дальнешего извлечения моделей
        self.mainPatternList = [(main_word_index, pattern) for pattern in pattternsMainWord]
        # список вида [(главное слово, модель управления)]
        self.dependentsList = dep
        self.unavailable = set()
        self.delete_variants_of_new_parsed(main_word_index)
        self.currentMain = None
        self.currentPattern = None
        self.currentDep = None
        self.currentMainPatternIndex = None # индекс текущей пары главное + модель в mainPatternList
        self.depDict = {} # по главному + модели возвращается DepWords
        self.flagEnd = False
        self.morphPosition = morphPosition
        self.wordPosition = wordPosition
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
        return

    def findPotentialMainPattern(self):
        # может быть три исхода 1. нашли, все ок
        # 2. надо заново запустить nextMainPattern, тк для найденной пары (главное, модель) нет зависимых
        # 3. больше нет пар
        numberOfBestPair = FindBestPatternInList(self.mainPatternList)
        if numberOfBestPair == None:
            return (None, None)
        (currentMain, currentPattern) = self.mainPatternList[numberOfBestPair]
        currentDep = self.getDepForNewPairMainPattern(currentMain, currentPattern)
        return (numberOfBestPair, currentDep)

    def nextMainPattern(self):
        '''Используется только для получения новой пары главное+модель, старая себя исчерпала'''
        # ищем пару (главное слово, модель) с максимальной оценкой(лучше 3 уровня, потом 2, потом 1)
        if self.currentMainPatternIndex != None:
            # удаляем пару (главное, модель) из списка и из словаря,
            # тк мы проверили для нее все зависимые, больше с ней ничего сделать нельзя
            self.mainPatternList.pop(self.currentMainPatternIndex)
        if (self.currentMain, self.currentPattern) in self.depDict.keys():
            self.depDict.pop((self.currentMain, self.currentPattern))
        (numberOfBestPair, currentDep) = self.findPotentialMainPattern()
        while (numberOfBestPair != None) and not (currentDep != None):
            # для данной пары (главное, модель) нет зависимых
            self.mainPatternList.pop(numberOfBestPair)
            (numberOfBestPair, currentDep) = self.findPotentialMainPattern()

        if numberOfBestPair == None:
            # больше списке пар self.mainPatternList нет вариантов
            self.flagEnd = True
            return None
        self.currentMainPatternIndex = numberOfBestPair
        (self.currentMain, self.currentPattern) = self.mainPatternList[numberOfBestPair]
        self.currentDep = currentDep
        return (self.currentMain, self.currentPattern)

    def get(self):
        if self.flagEnd:
            return None
        return (self.currentMain, self.currentPattern, self.currentDep.curDep[0], self.currentDep.curDep[1])

    def delete_variants_of_new_parsed(self, new_parsed):
        new_dependents_list = []
        for (cur_position, cur_variant) in self.dependentsList:
            if cur_position == new_parsed:
                self.unavailable.add((cur_position, cur_variant))
            else:
                new_dependents_list.append((cur_position, cur_variant))
        self.dependentsList = new_dependents_list

    def apply(self):
        '''currentDep - фиксируем, переводим его в main, удаляем из Dep все с данным зависимым'''
        newParsed = self.currentDep.curDep[0]
        self.addNewMainPatterns(self.currentDep.curDep)
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
        self.delete_variants_of_new_parsed(newParsed)
        delRes = self.currentDep.deleteInCurHalf(newParsed)
        if delRes != None:
            # для данной пары (главное, модель) еще могут быть зависимые(например, в случае однородности), сохраняем информацию о зависимых
            self.depDict[(self.currentMain, self.currentPattern)] = self.currentDep
        self.nextMainPattern()
        f.write("add " + str(newParsed))
        f.write("\n")
        f1.write("add " + str(newParsed))
        f1.write("\n")

    def create_dep(self, pattern, main_index):
        morph_constraints = pattern.get_dep_morph_constraints()
        word_constraints = pattern.get_dep_word()
        if not morph_constraints[0] in self.morphPosition.keys():
            return None
        itog_set = set(self.morphPosition[morph_constraints[0]])
        for i in range(1, len(morph_constraints)):
            if not morph_constraints[i] in self.morphPosition.keys():
                return None
            itog_set = itog_set.intersection(self.morphPosition[morph_constraints[i]])
        if word_constraints != None:
            if not word_constraints in self.wordPosition.keys():
                return None
            itog_set = itog_set.intersection(self.wordPosition[word_constraints])
        itog_set = itog_set.difference(self.unavailable)
        if itog_set == set():
            return None
        dep_posvars_for_constraints = sorted(itog_set)
        return DepWords(dep_posvars_for_constraints, main_index)

    def addNewMainPatterns(self, newMain):
        curMain = newMain[0]
        curVariant = newMain[1]
        patternsNewMain = self.allPatternsList[curMain][curVariant]
        mainPatternsNewMain = [(curMain, pattern) for pattern in patternsNewMain]
        self.mainPatternList += mainPatternsNewMain

    def getDepForNewPairMainPattern(self, newMain, newPattern):
        newKey = (newMain, newPattern)
        if newKey in self.depDict.keys():
            return self.depDict[newKey]
        else:
            currentDep = self.create_dep(newPattern, newMain)
            if currentDep != None:
                return currentDep
            else:
                return None # для новой модели нет зависимых, идем к следующей