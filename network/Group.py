import eventlet
import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.util import *

class Group:
    group_pool = {}
    def __init__(self, groupId=None):
        if Group.group_pool.get(groupId) is not None:
            print("Re-create groupId / groupId collision")
            raise Exception("Re-create groupId / groupId collision")
        self.conn_pool = []
        self.groupId = groupId
        self.desc = ""
        Group.group_pool[groupId] = self.conn_pool
        self.thread_pool = eventlet.GreenPool(config.CONN_THREAD_NUM)

    def set_desc(self, desc):
        self.desc = desc

    def thread_routine(self, conn):
        data = Pmd()
        while True:
            data.read_msg(conn)
            logging.info("%d threads running before broadcast" % self.thread_pool.running())
            self.thread_pool.imap(data.send_msg, self.conn_pool)
            logging.info("%d threads running after broadcast" % self.thread_pool.running())

    def add_conn(self, conn):
        self.conn_pool.append(conn)
        self.thread_pool.spawn(self.thread_routine, conn)