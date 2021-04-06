
from parse_point_module import Sentence
import copy

def parse(str1, count = 1):
    # toDo - а, если нет разбора ?
    s = Sentence(str1)
    ans = []
    for i in range(count):
        #print("------------------------------------------------------", i)
        res = s.sint_parse()
        if res is None:
            ans.append((None, None, s.view))
            break
        if res == "timeEnd":
            break
        trace_view_copy = copy.deepcopy(s.view)
        word_text_morph_list = []
        for choosing_word_variant in res.pp_words:
            word_text_morph_list.append((s.get_text(choosing_word_variant), s.get_word_parsing_variant(choosing_word_variant)))
        ans.append((word_text_morph_list, res.view, trace_view_copy))
    return ans
