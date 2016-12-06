import eventlet
import socket
from threading import Thread

import network.config as config
from network.util import *
from network.PMDatagram import PMDatagram as Pmd
from network.Group import Group
import pub_config as pc
from pub_config import FIELDS as fd


class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._group_pool = {}   # [group_id] => aGroup
        # self._idle_pool = {}
        self._main_thread = None

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.settimeout(0.5)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((config.HOST, config.PORT))
        self._server.listen(config.MAX)
        print("Connected")

    def run(self):
        self._main_thread = eventlet.spawn(self._accept_any)
        self._main_thread.wait()

    """Those who are connected and not yet in any group"""
    def _handle_any(self, conn):
        p = Pmd()
        print("_handle_idle")
        while True:
            d = p.read_json(conn)
            print(d)
            t = d.get(fd[0])
            if t is not None:
                if t == pc.GET_GROUPS:
                    p.send_groups(conn, self.get_group_info())
                elif t == pc.JOIN_GROUP:
                    self.join_group(d.get(fd["g"]), conn)
                elif t == pc.CREATE_GROUP:
                    self._add_group(d.get[fd["g"]])
                    self.join_group(d.get[fd["g"]], conn)
                elif t == pc.GET_GROUP_MEMBERS:
                    group_id = d.get(fd["g"])
                    if group_id is not None:
                        l = self.get_group_members(group_id)
                        if l is not None:
                            p.send_group_members(conn, group_id, l)

    """ with parameter check """
    def join_group(self, group_id, conn):
        group = self._group_pool.get(group_id)
        if group_id is None or group is None:
            warning_str = str(conn) + "Attempt to join invalid group " + str(group_id)
            print(warning_str)
            logging.warning(warning_str)
            return False
        group.add_conn(conn)

    def add_group(self, group_id):
        self._add_group(group_id)

    # Throws Exception
    def _add_group(self, group_id, name="Temporary Group", desc=""):
        if self._group_pool.get(group_id) is not None:
            warning_str = "Re-create group_id / groupId collision on " + str(group_id)
            print(warning_str)
            logging.warning(warning_str)
            return False
        g = Group(group_id=group_id, desc=desc, name=name)
        self._group_pool[group_id] = g
        return g

    """ Format [(group_id, name, n_members), ... ]"""
    def get_group_info(self):
        return [x.group_info() for x in self._group_pool.values()]

    """ Format [(user_id, user_name, user_desc), ... ]"""
    def get_group_members(self, group_id):
        g = self._group_pool.get(int(group_id))
        if g is None:
            warning_str = "Get users from invalid group ID " + str(group_id)
            print(warning_str)
            logging.warning(warning_str)
            return None
        return g.user_list()

    def _accept_any(self):
        self._server.settimeout(config.TIMEOUT)
        while True:
            conn = None
            address = None
            while conn is None:
                try:
                    conn, address = self._server.accept()
                except socket.timeout as t:
                    eventlet.sleep(config.TIMEOUT)
                    # conn, address = server.accept()
                    # handle(conn)
            print("Accepted" + str(address))
            eventlet.spawn_n(self._handle_any, conn)


if __name__ == "__main__":
    s = Server()
    s.start()
    s.add_group(8848)
    s.add_group(7737)
    s.add_group(6626)
    print(s.get_group_info())



