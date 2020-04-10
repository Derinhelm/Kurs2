import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

number_windows = 0
flag_control_tree = False

def on_mouse_click_tree(event, dict_parse_points, pos):
    # type: (matplotlib.backend_bases.MouseEvent) -> None
    global number_windows

    if event.dblclick:
        axes = event.inaxes

        # В качестве текущих выберем оси, внутри которых кликнули мышью
        plt.sca(axes)

        # Координаты клика в системе координат осей
        x = event.xdata
        y = event.ydata

        near_point = ""
        min_dist_2 = 100000000000
        for (word, (x_word, y_word)) in pos.items():
            cur_dist_2 = (x_word - x) ** 2 + (y_word - y) ** 2
            if cur_dist_2 < min_dist_2:
                near_point = word
                min_dist_2 = cur_dist_2
        parse_point = dict_parse_points[near_point]
        parse_point_visualize(parse_point, parse_point.__repr__())
        event.key = None
        plt.show()

def parse_tree_visualize(graph, dict_parse_points, title):
    '''visualizate tree of parse'''
    global number_windows
    number_windows += 1
    fig = plt.figure(number_windows)
    pos = graphviz_layout(graph, prog='dot')
    x_values, y_values = zip(*pos.values())
    x_max = max(x_values)
    x_min = min(x_values)
    x_margin = (x_max - x_min) * 0.25
    plt.xlim(x_min - x_margin, x_max + x_margin)
    y_max = max(y_values)
    y_min = min(y_values)
    y_margin = (y_max - y_min) * 0.25
    plt.ylim(y_min - y_margin, y_max + y_margin)
    fig.canvas.mpl_connect('button_press_event', lambda event: on_mouse_click_tree(event, dict_parse_points, pos))

    nx.draw_networkx_nodes(graph, pos, node_size=500, with_labels=True, node_color='silver')
    nx.draw(graph, pos, with_labels=True, arrows=False, node_size=1, horizontalalignment='center',
            verticalalignment='top', font_size=10, font_color='b')
    grafo_labels = nx.get_edge_attributes(graph, 'n')
    nx.draw_networkx_edge_labels(graph, pos, font_size=10, edge_labels=grafo_labels, label_pos=0.5, rotate=False)
    plt.title(title)
    plt.show()

def on_mouse_click_parse_point(event, parse_point, pos):
    # type: (matplotlib.backend_bases.MouseEvent) -> None
    if event.dblclick:
        # Координаты клика в системе координат осей
        x = event.xdata
        y = event.ydata
        near_word = ""
        min_dist_2 = 100000000000
        for (word, (x_word, y_word)) in pos.items():
            cur_dist_2 = (x_word - x) ** 2 + (y_word - y) ** 2
            if cur_dist_2 < min_dist_2:
                near_word = word
                min_dist_2 = cur_dist_2
        word_border = near_word.rfind('_')
        number_word = int(near_word[word_border+ 1:])
        text_word = near_word[:word_border]
        w = text_word + ' - ' + parse_point.parse_point_word_list[number_word].used_morph_answer.__repr__()
        global number_windows
        number_windows += 1
        plt.figure(number_windows, figsize=(0.5 + 0.12 * len(w),0.5)) # потом сделать возможность нескольких окон
        plt.axis('off')
        plt.text(0, 0.5, w, size = 15)
        plt.show()

def parse_point_visualize(parse_point, name):
        global number_windows
        number_windows += 1
        graph = parse_point.graph
        fig = plt.figure(number_windows)
        pos = graphviz_layout(graph, prog='dot')
        x_values, y_values = zip(*pos.values())
        x_max = max(x_values)
        x_min = min(x_values)
        x_margin = (x_max - x_min) * 0.25
        plt.xlim(x_min - x_margin, x_max + x_margin)
        y_max = max(y_values)
        y_min = min(y_values)
        y_margin = (y_max - y_min) * 0.25
        plt.ylim(y_min - y_margin, y_max + y_margin)
        fig.canvas.mpl_connect('button_press_event', lambda event: on_mouse_click_parse_point(event, parse_point, pos))
        nx.draw(graph, pos, with_labels=True, arrows=False, node_size=1, horizontalalignment='center',
                verticalalignment='top', font_size=20)
        plt.title(name)
        plt.show()

