#-*-coding:utf-8-*- 
__author__ = 'kanchan'
import sys
from PyQt5 import QtGui, Qt, QtCore
from PyQt5.QtWidgets import *
# from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMainWindow, QAction, qApp
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QCoreApplication
from util import *

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 100, 500, 300)
        self.setWindowTitle('hallo')

        # init tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('this is <b>Qwidget</b> widget')
        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)

        # init close bottuon
        # close_btn = QPushButton('Close', self)
        # close_btn.move(200, 50)
        # close_btn.resize(close_btn.sizeHint())
        # close_btn.setToolTip('Close')
        # close_btn.clicked.connect(QCoreApplication.instance().quit)

        # status bar on the bottom
        # self.statusBar().showMessage('Ready')

        self.initMenuBar()

        self.show()

    def initMenuBar(self):
        # init exit action
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exitAction)


class Chat_Box(QWidget):
    def __init__(self, username='Me'):
        super().__init__()
        self.username = username
        self.setGeometry(300, 100, 600, 400)
        self.setWindowTitle('hallo')
        self.user_label = QLabel('username:test@mail.com')
        self.room_id = QLabel('Room ID: 1234')

        # init chat content area
        bar = QWidget()
        self.text_box = QTextBrowser()
        self.text_box.addScrollBarWidget(QScrollBar(), Qt.Qt.AlignRight)

        # init input content area
        hinput = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.maximumSize()
        self.send_btn = QPushButton('Send')
        self.send_btn.setMaximumHeight(self.input_box.height())
        # send action
        self.send_btn.clicked.connect(self.send_msg)

        self.send_shortcut = QShortcut(QtGui.QKeySequence('Ctrl+Return'), self)
        self.send_shortcut.activated.connect(self.send_msg)
        # sendAction = QAction('&Send', self.send_btn)
        # sendAction.setShortcut('Cmd+Enter')
        # sendAction.setStatusTip('Send')
        hinput.addWidget(self.input_box, 10)
        hinput.addWidget(self.send_btn, 2)

        hbar = QHBoxLayout()
        hbar.addWidget(self.user_label, 1)
        hbar.addWidget(self.room_id, 1, Qt.Qt.AlignRight)
        # bar.setLayout(hbox)
        vbox = QVBoxLayout()
        vbox.addLayout(hbar)
        vbox.addWidget(bar, 0, Qt.Qt.AlignTop)
        vbox.addWidget(self.text_box, 80)
        vbox.addLayout(hinput, 20)

        self.setLayout(vbox)

        self.show()

    def show_msg(self, user, content):
        self.text_box.append('%s  %s:\n%s' % (user, get_time_str(), content))
        self.text_box.append('')

    def send_msg(self):
        self.show_msg(self.username, self.input_box.toPlainText())
        self.input_box.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat = Chat_Box()
    chat.show_msg('mzy', '你好哇..................................................')
    for i in range(5):
        chat.show_msg('ck', '你好哇， 傻逼')
    sys.exit(app.exec_())