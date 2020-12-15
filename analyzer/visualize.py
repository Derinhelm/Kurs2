import copy

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from matplotlib.backend_bases import MouseButton
from analyzer.patterns import GPattern
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
        plt.gcf().canvas.set_window_title("Слово")
        plt.show()

    def set_text(self, text):
        self.text = text


class PatternView:
    def __init__(self, pattern: GPattern = None):
        if pattern is None:
            self.text = 'Выбрано первое слово.'
            self.count_lines = 1
            self.max_len = len(self.text)
        else:
            s = "Модель " + str(pattern.level) + " уровня; \n"
            s += "оценка - " + str(pattern.get_mark()) + ";  \n"
            s_m_c = "требования на главное слово:" + ', '.join(pattern.main_word_constraints) + "; \n"
            s += s_m_c
            s_d_c = "требования на зависимое слово:" + ', '.join(pattern.dependent_word_constraints) + "; \n"
            s += s_d_c
            self.max_len = max(len(s_m_c), len(s_d_c))
            count_lines = 4
            if pattern.main_word is not None:
                s_m_w = "начальная форма главного - " + pattern.main_word + "; \n"
                s += s_m_w
                self.max_len = max(self.max_len, len(s_m_w))
                count_lines += 1
            if pattern.dependent_word is not None:
                s_d_w = "начальная форма зависимого - " + pattern.dependent_word + "; \n"
                s += s_d_w
                self.max_len = max(self.max_len, len(s_d_w))
                count_lines += 1
            self.count_lines = count_lines
            self.text = s[:-3]

    def visualize(self):
        global number_windows
        number_windows += 1
        plt.figure(number_windows, figsize=(0.5 + 0.12 * self.max_len, 0.4 * self.count_lines))
        #plt.figure(number_windows)
        plt.axis('off')
        plt.text(0, 0, self.text, size=15, horizontalalignment='left', verticalalignment='bottom')
        plt.gcf().canvas.set_window_title("Модель управление")
        plt.show()

    def set_text(self, text):
        self.text = text



class ParsePointView:
    def __init__(self, point_title, sent_title, words_count=None):
        self.graph = nx.DiGraph()
        self.sent_title = sent_title
        self.words_view = []
        self.point_label = 'root'
        for i in range(words_count):
            new_word_view = ParsePointWordView("not parsed")
            self.words_view.append(new_word_view)
        self.point_title = point_title
        self.status = 'intermediate'

    def change_word_view(self, word_position, word_info):
        self.words_view[word_position].set_text(word_info)

    def create_child_view(self, new_point, main_word, dep_word=None):
        child = copy.deepcopy(self)
        child.point_title = str(new_point)
        child.point_label = str(new_point.number_point)
        child.status = new_point.status
        main_title = main_word.word.word_text
        #main_title = main_word.word.word_text + "_" + str(main_word.number_in_sentence)
        if dep_word is None:
            # первая для разбора точка
            child.graph.add_node(main_title)
            child.change_word_view(main_word.number_in_sentence, main_word.get_form().__repr__())
        else:
            #dep_title = dep_word.word.word_text + "_" + str(dep_word.number_in_sentence)
            dep_title = dep_word.word.word_text

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
        usual_nodes = {n: n for n in self.graph.nodes if n[0].isalpha()}
        h_nodes = {n: n for n in self.graph.nodes if not n[0].isalpha()}
        plt.ylim(y_min - y_margin, y_max + y_margin)
        nx.draw(self.graph, pos, arrows=False, node_size=500, node_color='w',
                horizontalalignment='center', verticalalignment='center', font_size=12)
        nx.draw_networkx_labels(self.graph, pos, labels=usual_nodes,
                                font_color='black')
        nx.draw_networkx_labels(self.graph, pos, labels=h_nodes,
                                font_color='green')
        plt.title(self.sent_title)

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
        usual_nodes = {n:n for n in self.graph.nodes if n[0].isalpha()}
        h_nodes = {n:n for n in self.graph.nodes if not n[0].isalpha()}
        plt.ylim(y_min - y_margin, y_max + y_margin)
        fig.canvas.mpl_connect('button_press_event', lambda event: self.on_mouse_click_parse_point(event, pos))
        #nx.draw(self.graph, pos, with_labels=True, arrows=False, node_size=1, horizontalalignment='center',
        #        verticalalignment='top', font_size=20)
        nx.draw(self.graph, pos, font_color = 'black', arrows=False, node_size=1000, node_color='w',
                horizontalalignment='center', verticalalignment='center', font_size=20)
        nx.draw_networkx_labels(self.graph, pos, labels=usual_nodes,
                               font_color='black')
        nx.draw_networkx_labels(self.graph, pos, labels = h_nodes,
                               font_color='green')
        plt.title(self.sent_title, fontsize=14)
        plt.gcf().canvas.set_window_title("Точка разбора")
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

    def merge_homogeneous(self, homogeneous_nodes):
        '''В визуализации создаем узлы для однородных'''
        num = 1
        for main, h in homogeneous_nodes:
            self.graph.add_node(h.title)
            num += 1
            main_title = main.word.word_text
            for c in h.words:
                dep_title = c.dep_word.word.word_text
                self.graph.add_edge(h.title, dep_title)
                self.graph.remove_edge(main_title, dep_title)
            self.graph.add_edge(main_title, h.title)


class ParsePointTreeView:
    def __init__(self, title, root_view):
        self.dict_parse_points = {}  # словарь соответствия названия точки - ее view
        self.title = title
        self.graph = nx.DiGraph()
        self.dict_parse_points[root_view.point_title] = root_view
        self.dict_patterns = {}
        self.graph.add_node(root_view.point_label, color = 'black')
        self.vertcolors = ['black']
        self.edge_colors = []

    def add_edge(self, parent_view: ParsePointView, child_view: ParsePointView, pattern: GPattern = None, word_pair_text:str = None):
        if child_view.status == 'wrong':
            v_color = 'red'
        elif child_view.status == 'right':
            v_color = 'green'
        elif child_view.status == 'intermediate-close':
            v_color = 'orange'
        elif child_view.status == 'right_with_conjs':
            v_color = 'yellow'
        else:
            v_color = 'black'
        self.graph.add_node(child_view.point_label, color = v_color)

        if pattern is None:
            e_color = 'black'
            lev = -1
        else:
            lev = pattern.level
            if pattern.level == 1:
                e_color = 'blue'
            elif pattern.level == 2:
                e_color = 'violet'
            else:
                e_color = 'lightblue'

        if word_pair_text is None:
            self.graph.add_edge(parent_view.point_label, child_view.point_label, n="Разбор первого слова", lev = lev, color = e_color)
            #self.graph.add_edge(parent_view.point_label, child_view.point_label, n="", lev = lev, color = e_color)
            self.dict_patterns[(parent_view.point_label, child_view.point_label)] = PatternView()
        else:
            self.graph.add_edge(parent_view.point_label, child_view.point_label, n=word_pair_text, lev = lev, color = e_color)
            #self.graph.add_edge(parent_view.point_label, child_view.point_label, n="", lev = lev, color = e_color)
            self.dict_patterns[(parent_view.point_label, child_view.point_label)] = PatternView(pattern)
        self.dict_parse_points[child_view.point_label] = child_view
        self.edge_colors.append(e_color)


    def close_node(self, node_title):
        if self.graph.nodes[node_title]['color'] == 'black':
            self.graph.nodes[node_title]['color'] = 'orange'

    def find_near_word(self, x, y, pos):
        near_point = ""
        min_dist_2 = 100000000000
        for (word, (x_word, y_word)) in pos.items():
            cur_dist_2 = (x_word - x) ** 2 + (y_word - y) ** 2
            if cur_dist_2 < min_dist_2:
                near_point = word
                min_dist_2 = cur_dist_2
        return near_point


    def find_near_pattern(self, x, y, pos):

        # сначала ищем уровень клика, потом смотрим все ребра этого уровня
        pos_dict = {}
        for (beg_title, (x1, y1)) in pos.items():
            beg_coord = (x1, y1)
            for end_title in self.graph._succ[beg_title].keys():
                end_coord = pos[end_title]
                val = (beg_coord, end_coord, (beg_title, end_title))
                if y1 in pos_dict.keys():
                    pos_dict[y1].append(val)
                else:
                    pos_dict[y1] = [val]

        min_delta = 1000000
        near_y = -1
        for cur_y in pos_dict.keys():
            if cur_y >= y and cur_y - y < min_delta:
                near_y = cur_y
                min_delta = cur_y - y
        min_p = 100000000
        for ((x_beg, y_beg), (x_end, y_end), beg_end_pair) in pos_dict[near_y]:
            a = y_end - y_beg
            b = x_beg - x_end
            c = y_beg * x_end - x_beg * y_end
            p = abs(a * x + b * y + c) / (a ** 2 + b ** 2)**0.5
            if p < min_p:
                min_p = p
                near_edge = beg_end_pair
        return near_edge

    def on_mouse_click_tree(self, event, pos):
        global number_windows

        if event.dblclick:
            axes = event.inaxes

            # В качестве текущих выберем оси, внутри которых кликнули мышью
            plt.sca(axes)

            # Координаты клика в системе координат осей
            x = event.xdata
            y = event.ydata
            if event.button == MouseButton.LEFT:

                near_point = self.find_near_word(x, y, pos)
                parse_point_view = self.dict_parse_points[near_point]
                parse_point_view.visualize()
                #event.key = None
                plt.show()
            elif event.button == MouseButton.RIGHT:
                near_edge = self.find_near_pattern(x, y, pos)
                pattern_view = self.dict_patterns[near_edge]
                pattern_view.visualize()
                print(near_edge)
                print(pattern_view.text)
                #event.key = None
                plt.show()

    def visualize(self):
        """visualizate tree of parse"""
        global number_windows
        number_windows += 1
        #fig = plt.figure(number_windows, figsize=(30, 10))
        fig = plt.figure(number_windows, figsize=(20, 10))
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
        #nx.draw_networkx_nodes(self.graph, pos, node_size=500, with_labels=True)
        edge_colors = []
        color = nx.get_edge_attributes(self.graph, 'color')
        for edge in self.graph.edges():
            edge_colors.append(color[edge])
        nodecolors = []
        color_n = nx.get_node_attributes(self.graph, 'color')
        for node in self.graph.nodes():
            nodecolors.append(color_n[node])
        #nx.draw(self.graph, pos, with_labels=True, arrows=False, node_size=600, horizontalalignment='center', edge_color = edge_colors,
        #        verticalalignment='top', font_size=10, font_color='black', node_color='white', edgecolors = nodecolors, edgewidth = 8)
        nx.draw(self.graph, pos, with_labels=True, arrows=False, node_size=900, horizontalalignment='center',
                edge_color=edge_colors, verticalalignment='top', font_size=13, font_color='black', node_color='white', edgecolors=nodecolors,
                edgewidth=8)
        grafo_labels = nx.get_edge_attributes(self.graph, 'n')
        #nx.draw_networkx_edge_labels(self.graph, pos, font_size=10, edge_labels=grafo_labels, label_pos=0.3,
        #                             rotate=False)
        nx.draw_networkx_edge_labels(self.graph, pos, font_size=12, edge_labels=grafo_labels, label_pos=0.5,
                                     rotate=False)
        plt.title(self.title)
        plt.gcf().canvas.set_window_title("Дерево точек разбора")
        plt.show()