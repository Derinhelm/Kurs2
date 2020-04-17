import sys

import PyQt5.QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QDesktopWidget, QApplication, QLabel, QVBoxLayout, QPushButton,
                             QLineEdit)
import PyQt5.QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QListWidget, QWidget, QHBoxLayout, QDesktopWidget, QHeaderView, QSlider,
                             QApplication, QLabel, QGridLayout, QVBoxLayout, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem)
from main import parse
from parse_point_module import WordInSentence
from visualize import ParsePointView, ParsePointTreeView, ParsePointWordView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class BeginWindow(QWidget):
    def __init__(self, parent=None, first_flag=False):
        super().__init__(parent, Qt.Window)
        self.build(first_flag)

    def open_win(self):
        s = self.sentence.text()
        c = int(self.count.text())
        parse(s,c)
        end = ResWindow(self, s, c)
        self.close()
        end.show()

    def build(self, first_flag):
        sentence_title = QLabel("Предложение")
        self.sentence = QLineEdit()
        count_title = QLabel("Количество разборов")
        self.count = QLineEdit()

        hbox = QHBoxLayout()
        hbox.addWidget(sentence_title)
        hbox.addWidget(self.sentence)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(count_title)
        hbox2.addWidget(self.count)

        self.beginButton = QPushButton("Начать разбор")
        self.beginButton.setFont(PyQt5.QtGui.QFont("Times", 20, PyQt5.QtGui.QFont.Bold))
        self.beginButton.clicked.connect(self.open_win)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.beginButton)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)

        self.setGeometry(444, 300, 350, 300)
        self.center()
        self.setWindowTitle('Начало работы')
        if first_flag:
            self.show()

        return

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class ResWindow(QWidget):
    def __init__(self, parent, s, count):
        super().__init__(parent, Qt.Window)
        self.res = parse(s, count)
        #grid = QGridLayout()
        number_res = 0
        point_button = []
        tree_button = []
        '''for (t, point, tree) in self.res:
            text_title = QLabel(str(t))
            grid.addWidget(text_title, number_res, 0)
            point_button.append(QPushButton("Визуализировать точку разбора"))
            point_button[number_res].clicked.connect(lambda: self.vis_parse_point(number_res))
            grid.addWidget(point_button[number_res], number_res, 1)
            tree_button.append(QPushButton("Визуализировать дерево"))
            tree_button[number_res].clicked.connect(lambda: self.vis_tree(number_res))
            grid.addWidget(tree_button[number_res], number_res, 2)
            number_res += 1'''
        texts = QListWidget()
        items_list = []
        for r in self.res:
            t = []
            for el in r[0]:
                t.append(el.__repr__())
            items_list.append(str(t))
        texts.addItems(items_list)
        point_buttons = QListWidget()
        point_buttons.addItems([str(i) + ".Визуализировать точку разбора" for i in range(1, len(self.res) + 1)])
        point_buttons.itemClicked.connect(self.point_visualize)
        trees_buttons = QListWidget()
        trees_buttons.addItems([str(i) + ".Визуализировать дерево точек разбора" for i in range(1, len(self.res) + 1)])
        trees_buttons.itemClicked.connect(self.tree_visualize)
        hbox = QHBoxLayout()
        hbox.addWidget(texts)
        hbox.addWidget(point_buttons)
        hbox.addWidget(trees_buttons)
        self.setLayout(hbox)
        number_res = 0
        #self.setLayout(grid)
        QApplication.desktop()
        # self.setGeometry(0, 0, e.height(), e.width())
        self.setGeometry(444, 300, 800, 900)
        self.setWindowTitle('Результаты')

        self.center()

    def point_visualize(self, item):
        s = item.text()
        number = int(s[:s.find('.')]) - 1
        self.res[number][1].visualize()

    def tree_visualize(self, item):
        s = item.text()
        number = int(s[:s.find('.')]) - 1
        self.res[number][2].visualize()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def vis_parse_point(self, number_point):
        self.res[number_point][1].visualize()

    def vis_tree(self, number_point):
        self.res[number_point][2].visualize()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BeginWindow(first_flag=True)
    sys.exit(app.exec_())
