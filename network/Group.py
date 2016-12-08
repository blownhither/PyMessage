import eventlet
import random

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
        self._users = Users()       # TODO: queue need lock?
        self._broadcast_queue = []  # JSON Datagrams

        self._thread_pool = eventlet.GreenPool(config.POOL_SIZE)
        # Group._group_pool[group_id] = self._conn_pool

        self.msg_id = random.randint(0, 1e7)

    def set_desc(self, desc):
        self.desc = desc

    # def _broadcast_routine(self):
    #     while True:
    #         if len(self._broadcast_queue) != 0:
    #             data = self._broadcast_queue.pop(0)
    #             conns = self._users.all_conns()
    #             p = Pmd(data=data)
    #             self._thread_pool.imap(p.send_json, conns)

    def _broadcast(self, datagram):
        p = Pmd(data=datagram)
        conns = self._users.all_conns()
        self._thread_pool.imap(p.send_json, conns)

    def add_user(self, conn, user_id, user_name, user_desc=None):
        try:
            return self._users.add_user(conn, user_id, user_name, user_desc)
        except Exception as e:
            log_str = "Adding user %d(%s) failed\n%s\n" % (user_id, user_name, str(e))
            print(log_str)
            logging.exception(log_str)
            return False


    def add_msg(self, conn, datagram):
        user_id = datagram["u"]
        if not self._users.validate_user(conn=conn, user_id=user_id):
            raise InvalidUserIDException()
        datagram[fd[0]] = pc.SERVER_SEND_MSG
        datagram[fd[2]] = self.msg_id
        datagram[fd["UserName"]] = self._users[user_id][1]
        self.msg_id += 1
        datagram[fd["Time"]] = encode_timestamp()
        self._broadcast(datagram)
        # self._broadcast_queue.append(datagram)

    """ Format [(user_id, user_name, user_desc), ... ]"""
    def user_list(self):
        return self._users.all_users()

    def group_info(self):
        return self.group_id, self.name, self._users.user_count()

    def remove_user(self, user_id):
        user = self._users[user_id]
        if user is None:
            log_str = "Quit group: requester not exist "
            logging.error(log_str)
            dprint(log_str)
            return False
        self._users.remove_user(user_id)
        return True


class Users:
    """ Data about user identification and connection
        format {[user_id] = (conn, user_name, user_desc), ... }
    """

    def __init__(self):
        self._all_users = {}

    def __getitem__(self, item):            # used as user[user_id]
        return self._all_users.get(item)

    def add_user(self, conn, user_id, user_name=None, user_desc=None):
        if user_id in self._all_users.keys():   # having joined
            log_str = "User %d(%s) trying to join a group again" % (user_id, user_name)
            logging.warning(log_str)
            t = self._all_users[user_id]
            if t[0] != conn:    # same ID, diff conn
                return False
            # still be able to add, can be used as rename
        if user_name is None:
            user_name = str(user_id)
        if user_desc is None:
            user_desc = str(user_id)
        self._all_users[user_id] = (conn, user_name, user_desc)
        return True

    def remove_user(self, user_id):
        if user_id not in self._all_users.keys():
            raise InvalidUserIDException()
        self._all_users.pop(user_id)

    def validate_user(self, conn, user_id, user_name=None):
        t = self._all_users.get(user_id)
        if t is None:
            return False
        if t[0] != conn:
            return  False
        if user_name is not None and user_name != t[1]:
            return False
        return True


    def all_conns(self):
        return [x[0] for x in self._all_users.values()]

    def all_users(self):
        return [(x, y[1], y[2]) for x, y in self._all_users.items()]

    def user_count(self):
        return len(self._all_users)


class InvalidUserIDException(Exception):
    pass


class InvalidGroupIDException(Exception):
    pass