import sys

import PyQt5.QtGui
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QListWidget, QWidget, QHBoxLayout, QDesktopWidget, QHeaderView,
                             QApplication, QLabel, QGridLayout, QVBoxLayout, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QButtonGroup, QScrollArea)
from PyQt5.QtGui import QPixmap
from main import parse
import functools
from parse_point_module import WordInSentence
from visualize import ParsePointView, ParsePointTreeView, ParsePointWordView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PIL import Image
class BeginWindow(QWidget):
    def __init__(self, parent=None, first_flag=False):
        super().__init__(parent, Qt.Window)
        self.build(first_flag)

    def open_win(self):
        s = self.sentence.text()
        c = int(self.count.text())
        end = ResWindow(self, s, c)
        self.close()
        end.show()
        x = 0
        self.destroy()


    def build(self, first_flag):
        sentence_title = QLabel("Предложение")
        sentence_title.setFont(PyQt5.QtGui.QFont("Times", 20, PyQt5.QtGui.QFont.Times))
        self.sentence = QLineEdit()
        self.sentence.setFont(PyQt5.QtGui.QFont("Times", 20, PyQt5.QtGui.QFont.Times))

        count_title = QLabel("Количество разборов")
        count_title.setFont(PyQt5.QtGui.QFont("Times", 20, PyQt5.QtGui.QFont.Times))
        self.count = QLineEdit()
        self.count.setFont(PyQt5.QtGui.QFont("Times", 20, PyQt5.QtGui.QFont.Times))

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

        self.setGeometry(444, 300, 800, 300)
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
        grid = QGridLayout()
        number_res = 0
        self.point_button = []
        self.tree_button = []
        for (t, point, tree) in self.res:
            if t != None:
                number_column = 0
                table = QTableWidget(self)
                table.setRowCount(2)
                table.setColumnCount(len(t))
                table.setWordWrap(True)
                table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                for number_column_t in range(len(t)):
                    w = t[number_column_t]
                    item = QTableWidgetItem(w.get_word_text())
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                    table.setItem(0, number_column_t, item)
                    x = str(w.get_morph()).replace("; ", "\n")
                    table.setItem(1, number_column_t, QTableWidgetItem(x))
                table.verticalHeader().hide()
                #text_title = QLabel(s)


                #text_title.setWordWrap(True)
                table.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
                #table.setFixedSize(len(t) * 100, 2 * 100)
                grid.addWidget(table, number_res, number_column)

                number_column += 1
                t = point.easy_visualize()
                lbl = QLabel(self)
                lbl.setPixmap(QPixmap(t))
                #lbl.setFixedWidth(500)
                grid.addWidget(lbl, number_res, number_column)
                #os.remove(t)

                number_column += 1
                self.point_button.append(QPushButton("Визуализировать точку разбора"))
                self.point_button[number_res].clicked.connect(functools.partial(self.point_vis, number = number_res))
                self.point_button[number_res].setFixedWidth(250)
                grid.addWidget(self.point_button[number_res], number_res, number_column)

                number_column += 1
                self.tree_button.append(QPushButton("Визуализировать дерево"))
                self.tree_button[number_res].clicked.connect(functools.partial(self.tree_vis, number = number_res))
                self.tree_button[number_res].setFixedWidth(250)

                grid.addWidget(self.tree_button[number_res], number_res, number_column)
                number_res += 1
            else:
                number_column = 0
                s = "Больше вариантов разбора нет. "
                text_title = QLabel(s)
                text_title.setFixedWidth(400)
                text_title.setWordWrap(True)
                text_title.setFont(PyQt5.QtGui.QFont("Times", 20, PyQt5.QtGui.QFont.Bold))
                grid.addWidget(text_title, number_res, number_column)

                number_column += 3
                self.tree_button.append(QPushButton("Визуализировать дерево"))
                self.tree_button[number_res].clicked.connect(functools.partial(self.tree_vis, number=number_res))
                self.tree_button[number_res].setFixedWidth(250)

                grid.addWidget(self.tree_button[number_res], number_res, number_column)
                number_res += 1

        widg = QWidget()

        widg.setLayout(grid)

        scroll = QScrollArea()
        scroll.setWidget(widg)
        scroll.setWidgetResizable(True)

        box = QHBoxLayout()
        box.addWidget(scroll)

        self.setLayout(box)


        QApplication.desktop()
        # self.setGeometry(0, 0, e.height(), e.width())
        self.setGeometry(444, 300, 1800, 900)
        self.setWindowTitle('Результаты')

        self.center()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def point_vis(self, number):
        self.res[number][1].visualize()

    def tree_vis(self, number):
        self.res[number][2].visualize()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = BeginWindow(first_flag=True)
    sys.exit(app.exec_())
