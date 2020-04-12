import sys

import PyQt5.QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QDesktopWidget, QApplication, QLabel, QVBoxLayout, QPushButton,
                             QLineEdit)

from main import easy_parse


class BeginWindow(QWidget):
    def __init__(self, parent=None, first_flag=False):
        super().__init__(parent, Qt.Window)
        self.build(first_flag)

    def open_win(self):
        s = self.sentence.text()
        self.close()
        for i in range(int(self.count.text())):
            easy_parse(s)

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


app = QApplication(sys.argv)
window = BeginWindow(first_flag=True)
sys.exit(app.exec_())
