
from parse_point_module import Tree
import copy

def parse(str1, count = 1):
    # toDo - а, если нет разбора ?
    t = Tree(str1)
    results = []
    ans = []
    for i in range(count):
        #print("------------------------------------------------------", i)
        try:
            new_parse = t.sint_parse()

        except StopIteration: # Больше вариантов разбора нет
            break

        else:
            if new_parse is None:
                ans.append((None, None, t.view))
                break

            # Проверка, что такого разбора предложения еще не было
            parse_is_new = True
            for exist_parse in results:
                if new_parse == exist_parse:
                    parse_is_new = False
                    break

            #TODO: ввести статус точки разбора в дереве точек разбора - такая уже была
            if parse_is_new:
                trace_view_copy = copy.deepcopy(t.view)
                word_text_morph_list = []
                for choosing_word_variant in new_parse.pp_words:
                    word_text_morph_list.append((t.get_text(choosing_word_variant), t.get_word_parsing_variant(choosing_word_variant)))
                ans.append((word_text_morph_list, new_parse.view, trace_view_copy))
                results.append(new_parse)

    return ans
