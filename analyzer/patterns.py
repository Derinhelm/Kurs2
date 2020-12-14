class GPattern:
    def __init__(self, level, mw, dw, mark, mc, dc):
        self.level = level
        self.main_word = mw
        self.dependent_word = dw
        self.mark = mark
        self.main_word_constraints = mc  # массив ограничений на морф
        self.dependent_word_constraints = dc  # массив ограничений на морф

    # здесь уже не может быть в ограничениях _any

    def get_mark(self):
        return round(self.mark)

    def __repr__(self):
        s = str(self.level) + ":"
        if self.level == 3:
            s += " " + self.dependent_word
        s += " " + str(round(self.get_mark())) + " "
        for c in self.dependent_word_constraints:
            s += " " + c + ";"
        return s

    def __lt__(self, other):  # x < y
        if self.level < other.level:
            return True
        if self.level > other.level:
            return False
        return self.mark < other.mark

    def get_dep_morph_constraints(self):
        return self.dependent_word_constraints

    def get_dep_word(self):
        return self.dependent_word

    def is_identical_dif_level(self, other):
        # модели разных уровней но с одинаковыми требованиями(мб какие-то требов. на главное/зависимое - None)
        if self.main_word_constraints != other.main_word_constraints:
            return False
        if self.dependent_word_constraints != other.dependent_word_constraints:
            return False

        if self.main_word is not None and other.main_word is not None and self.main_word != other.main_word:
            return False

        if self.dependent_word is not None and other.dependent_word is not None and self.dependent_word != other.dependent_word:
            return False

        return True

    def is_extended(self, other):
        # модели одинаковые (с точностью до уровня), но у self больше требований на главное слово


        if self.main_word is not None and other.main_word is not None and self.main_word != other.main_word:
            return False

        if self.dependent_word is not None and other.dependent_word is not None and self.dependent_word != other.dependent_word:
            return False

        if self.dependent_word_constraints != other.dependent_word_constraints:
            return False

        self_main_set = set(self.main_word_constraints)
        other_main_set = set(other.main_word_constraints)
        return other_main_set.issubset(self_main_set)
