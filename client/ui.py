#-*-coding:utf-8-*- 
__author__ = 'kanchan'
import sys

from PyQt5 import QtGui, Qt
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from client.util import *
import socket
import json, pub_config, eventlet
from network.Client import Client


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 100, 300, 400)
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
        self.show()


class GroupListItem(QListWidgetItem):
    def __init__(self, group_id, group_name, group_n_members):
        super().__init__()
        self.group_id = group_id
        self.group_name = group_name
        self.group_n_members = group_n_members

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
        self.group_id_edit = QLineEdit()
        self.enter_group_btn = QPushButton('Enter Chatting Group')
        self.enter_group_btn.clicked.connect(self.enterGroup)
        self.hbox2.addWidget(self.group_id_edit)
        self.hbox2.addWidget(self.enter_group_btn)
        self.enter_group_shortcut = QShortcut(QtGui.QKeySequence('Return'), self)
        self.enter_group_shortcut.activated.connect(self.enterGroup)

        self.group_list = QListWidget()
        # l = ['G01', 'G02', 'G03']
        # self.group_list.addItems(l)
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

        self.chats_pool = {}

        self.client = None
        if self.connect_server():
            self.refresh_group_list()
            self.fetch_msg()
            self.userId = self.client.get_user_id()

    def connect_server(self):
        try:
            self.client = Client()
            self.client.start()
        except Exception as e:
            return False
        return True

    def refresh_group_list(self):
        """
        .get_groups:    -> [(group_id, name, n_members), ... ]
        :return:
        """
        group_list = self.client.get_groups()
        group_id_list = [g[0] for g in group_list]
        for item in self.group_list.findItems('', Qt.Qt.MatchContains):
            if item.group_id not in group_id_list:
                self.group_list.removeItemWidget(item)
        group_id_list = [item.group_id for item in self.group_list.findItems('', Qt.Qt.MatchContains)]
        for g in group_list:
            if g[0] in group_id_list:
                continue
            item = GroupListItem(group_id=g[0], group_name=g[1], group_n_members=g[2])
            item.setText(item.group_name)
            self.group_list.addItem(item)

        QTimer.singleShot(5000, self.refresh_group_list)

    def fetch_msg(self):
        msg_list = self.client.read_msg(False)
        if msg_list is not None:
            print(msg_list)
        if msg_list is not None:
            msg_list = sorted(msg_list, key=lambda x: x['time'])
            for msg in msg_list:
                if msg['userId'] != self.userId:
                    self.chats_pool[msg['groupId']].show_msg(user=msg['userName'], content=msg['msg'])
        QTimer.singleShot(50, self.fetch_msg)

    def group_list_item_changed(self, current, previous):
        if current is None:
            return
        self.seleted_group = current
        self.group_id_edit.setText(current.group_name)

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
        if self.group_id_edit.text() == '':
            return
        # self.chat = Chat_Box.create_chat_box(username=self.username, group_id=self.group_id.text())
        # if self.chat.sock is None:
        #     self.chat = None
        self.chats_pool[self.seleted_group.group_id] = Chat_Box(username=self.username,
                                                                group_id=self.seleted_group.group_id,
                                                                group_name=self.seleted_group.group_name,
                                                                client=self.client)
        # self.chats_pool[self.seleted_group.group_id].client = self.client
        self.client.join_group(group_id=self.seleted_group.group_id, alias=self.username)

        # if self.chat is not None:
        #     self.chat.show_msg('mzy', '你好哇..................................................')
        #     for i in range(5):
        #         self.chat.show_msg('ck', '你好哇， 傻逼')
        # else:
        #     msg = QMessageBox()
        #     msg.setWindowTitle('Connect Failed')
        #     msg.setText("Group ID: %s \nCan't connect to server now, please try later." % self.group_id.text())
        #     msg.exec_()
        #     self.group_id.setText('')


class Chat_Box(QWidget):
    __opened_groups__ = set()

    @classmethod
    def create_chat_box(cls, username=None, group_id=None):
        if group_id in cls.__opened_groups__ or group_id is None or username is None:
            return None
        return Chat_Box(username, group_id)

    def __init__(self, username='Me', group_id=None, group_name=None, client=None):
        super().__init__()
        self.__opened_groups__.add(group_id)
        self.username = username
        self.group_id = group_id
        self.group_name = group_name
        self.setGeometry(620, 100, 700, 400)
        self.setWindowTitle('hallo')
        self.user_label = QLabel('username:%s' % self.username)
        self.room_id = QLabel('Room ID: %s' % self.group_id)
        self.client = client

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
        # self.friends_list.addItems(['mzy@gmail.com', 'sb@gmail.com', 'wdy@fudan.edu.cn'])

        self.all_layout_box = QHBoxLayout()
        self.all_layout_box.addLayout(self.vbox, 3)
        self.all_layout_box.addWidget(self.friends_list, 1)

        self.setLayout(self.all_layout_box)

        self.show()

        self.refresh_member_list()

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # try_count = 5
        # success = False
        # while try_count > 0 and not success:
        #     try_count -= 1
        #     try:
        #         self.sock.connect(('127.0.0.1', 8888))
        #         success = True
        #         eventlet.spawn(self.connect_handler)
        #     except Exception as e:
        #         print('Connect failed')
        # if not success:
        #     self.sock = None
    #
    # def connect_handler(self):
    #     try:
    #         while True:
    #             data = self.sock.recv(65536)
    #             data = json.loads(data)
    #             eventlet.sleep(0)
    #             if data['type'] == pub_config.SERVER_SEND_MSG:
    #                 self.show_msg(user=data['sender'], content=data['content'])
    #             elif data['type'] == pub_config.RETURN_GROUP_MEMBERS:
    #                 self.refresh_member_list(data['members'])
    #     except Exception as e:
    #         self.sock.close()

    def refresh_member_list(self):
        member_list = self.client.get_group_members(self.group_id)
        if member_list is not None:
            print(member_list)
            self.friends_list.clear()
            for (user_id, user_name, user_desc) in member_list:
                self.friends_list.addItem(user_name + '#' + str(user_id))
        # self.friends_list.clear()
        # self.friends_list.addItems(member_list)
        QTimer.singleShot(1000, self.refresh_member_list)

    def show_msg(self, user, content):
        self.text_box.append('%s  %s:\n%s' % (user, get_time_str(), content))
        self.text_box.append('')

    def send_msg(self):
        self.client.put_msg(self.input_box.toPlainText(), group_id=self.group_id)
        self.show_msg(self.username, self.input_box.toPlainText())
        self.input_box.setText('')

    def __del__(self):
        self.__opened_groups__.remove(self.group_id)
        self.client.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    # chat = Chat_Box()
    sys.exit(app.exec_())