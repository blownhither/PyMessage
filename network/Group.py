import eventlet
import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.util import *
import pub_config as pc
from pub_config import FIELDS as fd

class Group:
    # _group_pool = {}
    server = None

    def __init__(self, group_id=None, desc="", name=""):
        # if Group._group_pool.get(group_id) is not None:
        #     print("Re-create groupId / groupId collision")
        #     raise Exception("Re-create groupId / groupId collision")
        self._conn_pool = []
        self.group_id = group_id
        self.desc = desc
        self.name = name
        # Group._group_pool[group_id] = self._conn_pool
        self._thread_pool = eventlet.GreenPool(config.CONN_THREAD_NUM)

    def set_desc(self, desc):
        self.desc = desc

    def thread_routine(self, conn):
        data = Pmd()
        while True:
            data.read_raw_msg(conn)
            self._thread_pool.imap(data.send_raw_msg, self._conn_pool)

    def add_conn(self, conn):
        self._conn_pool.append(conn)
        self._thread_pool.spawn(self.thread_routine, conn)

    def conn_exit(self):
        # TODO:
        pass

    def report_info(self):
        return self.group_id, self.name, len(self._conn_pool)

    def conn_count(self):
        return len(self._conn_pool)