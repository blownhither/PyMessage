#-*-coding:utf-8-*- 
__author__ = 'kanchan'
import sys

from PyQt5 import QtGui, Qt
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from client.util import *
import socket
import json, pub_config


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
        if self.group_id.text() == '':
            return
        self.chat = Chat_Box.create_chat_box(username=self.username, group_id=self.group_id.text())
        if self.chat.sock is None:
            self.chat = None

        if self.chat is not None:
            self.chat.show_msg('mzy', '你好哇..................................................')
            for i in range(5):
                self.chat.show_msg('ck', '你好哇， 傻逼')
        else:
            msg = QMessageBox()
            msg.setWindowTitle('Connect Failed')
            msg.setText("Group ID: %s \nCan't connect to server now, please try later." % self.group_id.text())
            msg.exec_()
        self.group_id.setText('')

    def refresh_friend_list(self):
        # timer = QTimer()
        # timer.timeout.
        pass


class Chat_Box(QWidget):
    __opened_groups__ = set()

    @classmethod
    def create_chat_box(cls, username=None, group_id=None):
        if group_id in cls.__opened_groups__ or group_id is None or username is None:
            return None
        return Chat_Box(username, group_id)

    def __init__(self, username='Me', group_id=None):
        super().__init__()
        self.__opened_groups__.add(group_id)
        self.username = username
        self.group_id = group_id
        self.setGeometry(620, 100, 700, 400)
        self.setWindowTitle('hallo')
        self.user_label = QLabel('username:%s' % self.username)
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
        # self.send_shortcut = QShortcut(self)
        # self.send_shortcut.setKey(QtGui.QKeySequence('Ctrl+Return'))
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

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try_count = 5
        success = False
        while try_count > 0 and not success:
            try_count -= 1
            try:
                self.sock.connect(('127.0.0.1', 8888))
                success = True
            except Exception as e:
                print('Connect failed')
        if not success:
            self.sock = None

    def connect_handler(self):
        try:
            while True:
                data = self.sock.recv(65536)
                data = json.loads(data)
                if data['type'] == pub_config.SERVER_SEND_MSG:
                    self.show_msg(user=data['sender'], content=data['content'])
                elif data['type'] == pub_config.RETURN_GROUP_MEMBERS:
                    self.refresh_member_list(data['members'])
        except Exception as e:
            self.sock.close()

    def refresh_member_list(self, member_list):
        self.friends_list.clear()
        self.friends_list.addItems(member_list)
        pass

    def show_msg(self, user, content):
        if user == self.username:
            return
        self.text_box.append('%s  %s:\n%s' % (user, get_time_str(), content))
        self.text_box.append('')

    def send_msg(self):
        data = {
            'type': pub_config.CLIENT_SEND_MSG,
            'sender': self.username,
            'content': self.input_box.toPlainText()
        }
        data = json.dumps(data)
        self.sock.send(data)
        self.show_msg(self.username, self.input_box.toPlainText())
        self.input_box.setText('')

    def __del__(self):
        self.__opened_groups__.remove(self.group_id)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    # chat = Chat_Box()
    sys.exit(app.exec_())