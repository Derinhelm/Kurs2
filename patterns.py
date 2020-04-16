class GPattern:
    def __init__(self, level, mw, dw, mark, mc, dc):
        self.level = level
        self.main_word = mw
        self.dependent_word = dw
        self.mark = mark
        self.main_word_constraints = mc  # массив ограничений на морф
        self.dependent_word_constraints = dc  # массив ограничений на морф

    # здесь уже не может быть в ограничениях _any

    def __repr__(self):
        s = str(self.level) + ":"
        if self.level == 3:
            s += " " + self.dependent_word
        s += " " + str(self.mark) + " "
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
