
from sentence_module import Sentence


def parse(str1, count=1, need_trace=False):
    s = Sentence(str1)
    res = None
    for i in range(count):
        print("------------------------------------------------------", i)
        res = s.sint_parse()
        if need_trace:
            s.view.visualize()
        res.view.visualize()
    return res.parse_point_word_list


def easy_parse(s, count=1):
    parse(s, count, True)
# print(a1)
