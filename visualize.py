import copy

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

number_windows = 0


class ParsePointWordView:
    def __init__(self, text):
        self.text = text  #

    def visualize(self):
        global number_windows
        number_windows += 1
        plt.figure(number_windows, figsize=(0.5 + 0.12 * len(self.text), 0.5))
        plt.axis('off')
        plt.text(0, 0.5, self.text, size=15)
        plt.show()

    def set_text(self, text):
        self.text = text


class ParsePointView:
    def __init__(self, point_title, sent_title, words_count=None):  # toDo сделать проход по ParsePoint ?
        self.graph = nx.DiGraph()
        self.sent_title = sent_title
        self.words_view = []
        for i in range(words_count):
            new_word_view = ParsePointWordView("not parsed")
            self.words_view.append(new_word_view)
        self.point_title = point_title

    def change_word_view(self, word_position, word_info):
        self.words_view[word_position].set_text(word_info)

    def create_child_view(self, point_title, main_word, dep_word=None):
        child = copy.deepcopy(self)
        child.point_title = point_title
        main_title = main_word.word.word_text + "_" + str(main_word.number_in_sentence)
        if dep_word is None:
            # первая для разбора точка
            child.graph.add_node(main_title)
            child.change_word_view(main_word.number_in_sentence, main_word.get_form().__repr__())
        else:
            dep_title = dep_word.word.word_text + "_" + str(dep_word.number_in_sentence)
            child.graph.add_node(dep_title)
            child.graph.add_edge(main_title, dep_title)
            child.change_word_view(dep_word.number_in_sentence, dep_word.get_form().__repr__())
        return child

    def easy_visualize(self):
        global number_windows
        number_windows += 1
        fig = plt.figure(number_windows)
        pos = graphviz_layout(self.graph, prog='dot')
        for (k, v) in pos.items():
            pos[k] = (v[0] * 10, v[1])
        x_values, y_values = zip(*pos.values())
        x_max = max(x_values)
        x_min = min(x_values)
        x_margin = (x_max - x_min) * 0.4
        plt.xlim(x_min - x_margin, x_max + x_margin)
        y_max = max(y_values)
        y_min = min(y_values)
        y_margin = (y_max - y_min) * 0.25
        plt.ylim(y_min - y_margin, y_max + y_margin)
        nx.draw(self.graph, pos, with_labels=True, arrows=False, node_size=1, horizontalalignment='center',
                verticalalignment='top', font_size=12)
        plt.title(self.sent_title)

        # w1, h1 = fig.canvas.get_width_height()
        # buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
        # buf.shape = (w1, h1, 4)

        # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
        # buf = numpy.roll(buf, 3, axis=2)
        # w, h, d = buf.shape
        # return Image.fromstring("RGBA", (w, h), buf.tostring())
        t = '_' + str(number_windows)
        plt.savefig(t)
        plt.close()
        return t

    def visualize(self):
        global number_windows
        number_windows += 1
        fig = plt.figure(number_windows)
        pos = graphviz_layout(self.graph, prog='dot')
        x_values, y_values = zip(*pos.values())
        x_max = max(x_values)
        x_min = min(x_values)
        x_margin = (x_max - x_min) * 0.4
        plt.xlim(x_min - x_margin, x_max + x_margin)
        y_max = max(y_values)
        y_min = min(y_values)
        y_margin = (y_max - y_min) * 0.25
        plt.ylim(y_min - y_margin, y_max + y_margin)
        fig.canvas.mpl_connect('button_press_event', lambda event: self.on_mouse_click_parse_point(event, pos))
        nx.draw(self.graph, pos, with_labels=True, arrows=False, node_size=1, horizontalalignment='center',
                verticalalignment='top', font_size=20)
        plt.title(self.sent_title)
        fig.canvas.draw_idle()
        plt.show()

    def on_mouse_click_parse_point(self, event, pos):
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
            number_word = int(near_word[word_border + 1:])
            self.words_view[number_word].visualize()


class ParsePointTreeView:
    def __init__(self, title, root_view):
        self.dict_parse_points = {}  # словарь соответствия названия точки - ее view
        self.title = title
        self.graph = nx.DiGraph()
        self.dict_parse_points[root_view.point_title] = root_view
        self.graph.add_node(root_view.point_title)

    def add_edge(self, parent_view: ParsePointView, child_view: ParsePointView, pattern: str = None):
        self.graph.add_node(child_view.point_title)
        if pattern is None:
            self.graph.add_edge(parent_view.point_title, child_view.point_title, n="first word")
        else:
            self.graph.add_edge(parent_view.point_title, child_view.point_title, n=pattern)
        self.dict_parse_points[child_view.point_title] = child_view

    def on_mouse_click_tree(self, event, pos):
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
            parse_point_view = self.dict_parse_points[near_point]
            parse_point_view.visualize()
            event.key = None
            plt.show()

    def visualize(self):
        """visualizate tree of parse"""
        global number_windows
        number_windows += 1
        fig = plt.figure(number_windows)
        pos = graphviz_layout(self.graph, prog='dot')
        x_values, y_values = zip(*pos.values())
        x_max = max(x_values)
        x_min = min(x_values)
        x_margin = (x_max - x_min) * 0.25
        plt.xlim(x_min - x_margin, x_max + x_margin)
        y_max = max(y_values)
        y_min = min(y_values)
        y_margin = (y_max - y_min) * 0.25
        plt.ylim(y_min - y_margin, y_max + y_margin)
        fig.canvas.mpl_connect('button_press_event', lambda event: self.on_mouse_click_tree(event, pos))

        nx.draw_networkx_nodes(self.graph, pos, node_size=500, with_labels=True, node_color='silver')
        nx.draw(self.graph, pos, with_labels=True, arrows=False, node_size=1, horizontalalignment='center',
                verticalalignment='top', font_size=10, font_color='b')
        grafo_labels = nx.get_edge_attributes(self.graph, 'n')
        nx.draw_networkx_edge_labels(self.graph, pos, font_size=10, edge_labels=grafo_labels, label_pos=0.5,
                                     rotate=False)
        plt.title(self.title)
        plt.show()
