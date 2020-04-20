import sys

import PyQt5.QtGui
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLineEdit, QListWidget, QWidget, QHBoxLayout, QDesktopWidget, QHeaderView, QSlider,
                             QApplication, QLabel, QGridLayout, QVBoxLayout, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QButtonGroup)
from PyQt5.QtGui import QPixmap
from main import parse
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
        grid = QGridLayout()
        number_res = 0
        self.point_button = []
        self.tree_button = []
        for (t, point, tree) in self.res:
            number_column = 0
            text_title = QLabel(str(t))
            grid.addWidget(text_title, number_res, number_column)
            number_column += 1
            t = point.easy_visualize()
            lbl = QLabel(self)
            lbl.setPixmap(QPixmap(t))
            grid.addWidget(lbl, number_res, number_column)
            #os.remove(t)

            number_column += 1
            self.point_button.append(QPushButton("Визуализировать точку разбора"))
            self.point_button[number_res].clicked.connect(lambda i: self.res[i][1].visualize(), number_res)
            grid.addWidget(self.point_button[number_res], number_res, number_column)

            number_column += 1
            self.tree_button.append(QPushButton("Визуализировать дерево"))
            self.tree_button[number_res].clicked.connect(lambda i: self.res[i][2].visualize(), number_res)

            grid.addWidget(self.tree_button[number_res], number_res, number_column)
            number_res += 1

        self.setLayout(grid)




        QApplication.desktop()
        # self.setGeometry(0, 0, e.height(), e.width())
        self.setGeometry(444, 300, 800, 900)
        self.setWindowTitle('Результаты')

        self.center()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def point_vis(self, number):
        point_view = self.res[number][1]
        fig = point_view.visualize()
        fig.canvas.draw_idle()
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = BeginWindow(first_flag=True)
    sys.exit(app.exec_())
