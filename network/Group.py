import eventlet
import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.util import *

class Group:
    _group_pool = {}

    def __init__(self, group_id=None):
        if Group._group_pool.get(group_id) is not None:
            print("Re-create groupId / groupId collision")
            raise Exception("Re-create groupId / groupId collision")
        self._conn_pool = []
        self.groupId = group_id
        self.desc = ""
        Group._group_pool[group_id] = self._conn_pool
        self.thread_pool = eventlet.GreenPool(config.CONN_THREAD_NUM)

    def set_desc(self, desc):
        self.desc = desc

    def thread_routine(self, conn):
        data = Pmd()
        while True:
            data.read_msg(conn)
            # logging.info("%d threads running before broadcast" % self.thread_pool.running())
            self.thread_pool.imap(data.send_msg, self._conn_pool)
            # logging.info("%d threads running after broadcast" % self.thread_pool.running())

    def add_conn(self, conn):
        self._conn_pool.append(conn)
        self.thread_pool.spawn(self.thread_routine, conn)
        print("Spawned")

    def conn_exit(self):
        # TODO:
        pass


    def conn_count(self):
        return len(self._conn_pool)