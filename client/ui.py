#-*-coding:utf-8-*- 
__author__ = 'kanchan'
import sys

from PyQt5 import QtGui, Qt
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from client.util import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 100, 300, 400)
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
        self.show()

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.username = 'hello@gmail.com'
        self.initUI()

    def initUI(self):
        # self.setGeometry(300, 100, 600, 600)
        # self.setWindowTitle('hallo')

        # init tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('this is <b>Qwidget</b> widget')

        # this hbox is for "New group" button and "Get groups" button
        self.hbox1 = QHBoxLayout()
        self.new_group_btn = QPushButton('New Group')
        self.get_groups_btn = QPushButton('Get My Groups')
        self.hbox1.addWidget(self.new_group_btn)
        self.hbox1.addWidget(self.get_groups_btn)

        # this hbox is for "Enter group"
        self.hbox2 = QHBoxLayout()
        self.group_id = QLineEdit()
        self.enter_group_btn = QPushButton('Enter Chatting Group')
        self.enter_group_btn.clicked.connect(self.enterGroup)
        self.hbox2.addWidget(self.group_id)
        self.hbox2.addWidget(self.enter_group_btn)
        self.enter_group_shortcut = QShortcut(QtGui.QKeySequence('Return'), self)
        self.enter_group_shortcut.activated.connect(self.enterGroup)

        self.group_list = QListWidget()
        l = ['G01', 'G02', 'G03']
        self.group_list.addItems(l)
        self.group_list.currentItemChanged.connect(self.group_list_item_changed)

        # init close bottuon
        self.close_btn = QPushButton('Close')
        self.close_btn.move(200, 50)
        self.close_btn.resize(self.close_btn.sizeHint())
        self.close_btn.setToolTip('Close')
        self.close_btn.clicked.connect(QCoreApplication.instance().quit)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbox1, 1)
        self.vbox.addWidget(self.group_list, 1)
        self.vbox.addLayout(self.hbox2, 1)
        self.vbox.addWidget(self.close_btn)

        # status bar on the bottom
        # self.statusBar().showMessage('Ready')
        # self.unsetLayoutDirection()
        self.setLayout(self.vbox)

        # self.initMenuBar()

        self.show()

    def group_list_item_changed(self, current, previous):
        self.group_id.setText(current.text())

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

    def enterGroup(self):
        self.chat = Chat_Box(username=self.username, group_id=self.group_id.text())
        self.group_id.setText('')

        self.chat.show_msg('mzy', '你好哇..................................................')
        for i in range(5):
            self.chat.show_msg('ck', '你好哇， 傻逼')


class Chat_Box(QWidget):
    def __init__(self, username='Me', group_id=None):
        super().__init__()
        self.username = username
        self.group_id = group_id
        self.setGeometry(620, 100, 700, 400)
        self.setWindowTitle('hallo')
        self.user_label = QLabel('username:test@mail.com')
        self.room_id = QLabel('Room ID: %s' % self.group_id)

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

        self.hbar = QHBoxLayout()
        self.hbar.addWidget(self.user_label, 1)
        self.hbar.addWidget(self.room_id, 1, Qt.Qt.AlignRight)
        # bar.setLayout(hbox)
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbar)
        self.vbox.addWidget(bar, 0, Qt.Qt.AlignTop)
        self.vbox.addWidget(self.text_box, 80)
        self.vbox.addLayout(hinput, 20)

        # self.friends_vbox = QVBoxLayout()
        self.friends_list = QListWidget()
        self.friends_list.addItems(['mzy@gmail.com', 'sb@gmail.com', 'wdy@fudan.edu.cn'])

        self.all_layout_box = QHBoxLayout()
        self.all_layout_box.addLayout(self.vbox, 3)
        self.all_layout_box.addWidget(self.friends_list, 1)

        self.setLayout(self.all_layout_box)

        self.show()

    def show_msg(self, user, content):
        self.text_box.append('%s  %s:\n%s' % (user, get_time_str(), content))
        self.text_box.append('')

    def send_msg(self):
        self.show_msg(self.username, self.input_box.toPlainText())
        self.input_box.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())