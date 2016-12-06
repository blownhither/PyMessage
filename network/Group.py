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
        # self._conn_pool = []
        self.group_id = group_id
        self.desc = desc
        self.name = name
        self._users = Users()
        self._broadcast_queue = []  # JSON Datagrams
        # Group._group_pool[group_id] = self._conn_pool
        self._thread_pool = eventlet.GreenPool(config.CONN_THREAD_NUM)

    def set_desc(self, desc):
        self.desc = desc

    def broadcast_routine(self, conn):
        while True:
            if len(self._broadcast_queue) != 0:
                data = self._broadcast_queue.pop(0)
                conns = self._users.all_conns()
                p = Pmd(data=data)
                self._thread_pool.imap(p.send_json, conns)

    def add_user(self, conn, user_id, user_name, user_desc):
        self._users.add_user(conn, user_id, user_name, user_desc)

    """ Format [(user_id, user_name, user_desc), ... ]"""

    def user_list(self):
        return self._users.all_users()

    def group_info(self):
        return self.group_id, self.name, self._users.user_count()

    def conn_exit(self):
        # TODO:
        pass


class Users:
    """ Data about user identification and connection
        format {[user_id] = (conn, user_name, user_desc), ... }
    """

    def __init__(self):
        self._all_users = {}

    def add_user(self, conn, user_id, user_name=None, user_desc=None):
        if user_id in self._all_users.keys():
            raise InvalidUserIDException()
        if user_name is None:
            user_name = str(user_id)
        if user_desc is None:
            user_desc = str(user_id)
        self._all_users[user_id] = (conn, user_name, user_desc)

    def remove_user(self, user_id):
        if user_id not in self._all_users.keys():
            raise InvalidUserIDException()
        self._all_users.pop(user_id)

    def all_conns(self):
        return [x[0] for x in self._all_users.values()]

    def all_users(self):
        return [(x, y[1], y[2]) for x, y in self._all_users.items()]

    def user_count(self):
        return len(self._all_users)


class InvalidUserIDException(Exception):
    pass
