import sys

import PyQt5.QtGui
import psycopg2
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QDesktopWidget, QHeaderView, QApplication, QLabel, QGridLayout,
                             QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem)

from analyzer.functions import get_patterns_pandas


class EndWindow(QWidget):
    def __init__(self, parent, df):
        # Передаём ссылку на родительский элемент и чтобы виджет
        # отображался как самостоятельное окно указываем тип окна
        super().__init__(parent, Qt.Window)

        grid = QGridLayout()

        headers = df.columns.values.tolist()
        table = QTableWidget()
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(headers)
        table.setWordWrap(True)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        for i, row in df.iterrows():

            for j in range(df.shape[1]):
                x = row[j]
                table.setItem(i, j, QTableWidgetItem(str(x)))
        #table.show()
        grid.addWidget(table, 0, 0)
        self.setLayout(grid)
        QApplication.desktop()
        self.resize(640, 400)
        self.setWindowTitle('Итог')

        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class BeginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.build()

    def open_win(self):
        level = int(self.level.text())
        main_word = self.main_word.text()
        if main_word == '':
            main_word = None
        dep_word = self.dep_word.text()
        if dep_word == '':
            dep_word = None
        main_morph_s = self.main_morph.text()
        if main_morph_s == '':
            main_morph = []
        else:
            main_morph = main_morph_s.split(', ')
        dep_morph_s = self.dep_morph.text()
        if dep_morph_s == '':
            dep_morph = []
        else:
            dep_morph = dep_morph_s.split(', ')
        con = psycopg2.connect(dbname='gpatterns_copy', user='postgres',
                               password='postgres', host='localhost')
        cursor = con.cursor()
        res = get_patterns_pandas(cursor, level, main_morph_params=main_morph, dep_morph_params=dep_morph,
                                  main_word_param=main_word, dep_word_param=dep_word)

        cursor.close()
        con.close()
        end_win = EndWindow(self, res)

        self.close()
        end_win.show()

    def build(self):

        vbox = QVBoxLayout()

        lev_title = QLabel("Уровень модели")
        lev_title.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        self.level = QLineEdit()
        self.level.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        self.level.textChanged.connect(self.block_word)
        hbox = QHBoxLayout()
        hbox.addWidget(lev_title)
        hbox.addWidget(self.level)

        main_word_title = QLabel("Главное слово")
        main_word_title.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        self.main_word = QLineEdit()
        self.main_word.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        dep_word_title = QLabel("Зависимое слово")
        dep_word_title.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        self.dep_word = QLineEdit()
        self.dep_word.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        hbox.addWidget(main_word_title)
        hbox.addWidget(self.main_word)
        hbox.addWidget(dep_word_title)
        hbox.addWidget(self.dep_word)

        vbox.addLayout(hbox)

        main_morph_title = QLabel("Морф. ограничения главного")
        main_morph_title.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        self.main_morph = QLineEdit()
        self.main_morph.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        dep_morph_title = QLabel("Морф. ограничения зависимого")
        dep_morph_title.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        self.dep_morph = QLineEdit()
        self.dep_morph.setFont(PyQt5.QtGui.QFont("Times", 18, PyQt5.QtGui.QFont.Times))
        hbox = QHBoxLayout()
        hbox.addWidget(main_morph_title)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.main_morph)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(dep_morph_title)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.dep_morph)
        vbox.addLayout(hbox)


        beginButton = QPushButton("Найти модели")
        beginButton.setFont(PyQt5.QtGui.QFont("Times", 20, PyQt5.QtGui.QFont.Bold))
        beginButton.clicked.connect(self.open_win)
        hbox = QHBoxLayout()
        hbox.addWidget(beginButton)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # self.setGeometry(444, 300, 350, 300)
        self.center()
        self.setWindowTitle('Начало работы')
        self.show()
        return

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def block_word(self):
        if self.level.text() == '1':
            self.main_word.setReadOnly(True)
            self.main_word.setStyleSheet("QLineEdit {background-color:lightgray}")
            self.dep_word.setReadOnly(True)
            self.dep_word.setStyleSheet("QLineEdit {background-color:lightgray}")

        elif self.level.text() == '2':
            self.dep_word.setReadOnly(True)
            self.dep_word.setStyleSheet("QLineEdit {background-color:lightgray}")
            self.main_word.setReadOnly(False)
            self.main_word.setStyleSheet("QLineEdit {background-color:white}")
        elif self.level.text() == '3':
            self.main_word.setReadOnly(False)
            self.main_word.setStyleSheet("QLineEdit {background-color:white}")
            self.dep_word.setReadOnly(False)
            self.dep_word.setStyleSheet("QLineEdit {background-color:white}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BeginWindow()
    sys.exit(app.exec_())
