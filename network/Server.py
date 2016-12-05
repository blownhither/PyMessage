import eventlet
import socket
from threading import Thread

import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.Group import Group
import pub_config as pc
from pub_config import FIELDS as fd


class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._group_pool = {}
        self._idle_pool = {}
        self._main_thread = None

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.settimeout(0.5)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((config.HOST, config.PORT))
        self._server.listen(config.MAX)
        print("Connected")

    def run(self):
        self._main_thread = eventlet.spawn(self._accept_any)
        print("Spawned")
        self._main_thread.wait()

    """Those who are connected and not yet in any group"""
    def _handle_idle(self, conn):
        while True:
            p = Pmd()
            d = p.read_json(self._server)
            print(d)
            t = d.get(fd[0])
            if t is not None and t == pc.GET_GROUPS:
                p.send_groups(self.get_group_info())

        # TODO: Use decent grouping here
        # g = self._add_group(8848)
        # g.add_conn(conn)
        # return

    def add_group(self, group_id):
        self._add_group(group_id)

    # Throws Exception
    def _add_group(self, group_id, name="Temporary Group", desc=""):
        if self._group_pool.get(group_id) is not None:
            print("Re-create group_id / groupId collision")
            raise Exception("Re-create groupId / groupId collision")
        g = Group(group_id=group_id, desc=desc, name=name)
        self._group_pool[group_id] = g
        return g

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
            eventlet.spawn_n(self._handle_idle, conn)

    def get_group_info(self):
        return [x.report_info() for x in self._group_pool.values()]


if __name__ == "__main__":
    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.settimeout(0.5)
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # server.bind((config.HOST, config.PORT))
    # server.listen(config.MAX)
    # print("Connected")
    # main_thread = eventlet.spawn(accept_any, server)
    # main_thread.wait()
    s = Server()
    s.start()
    s.add_group(1312)
    s.add_group(3215)
    print(s.get_group_info())
