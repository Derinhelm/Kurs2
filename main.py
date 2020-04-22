
from parse_point_module import Sentence
import copy

def parse(str1, count = 1):
    # toDo - а, если нет разбора ?
    s = Sentence(str1)
    ans = []
    for i in range(count):
        print("------------------------------------------------------", i)
        res = s.sint_parse()
        if res is None:
            break
        trace_view_copy = copy.deepcopy(s.view)
        ans.append((res.parse_point_word_list, res.view, trace_view_copy))
    return ans
