import eventlet
import socket
from threading import Thread

import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.Group import Group


class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.group_pool = {}
        self.idle_pool = {}
        self.main_thread = None

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.settimeout(0.5)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((config.HOST, config.PORT))
        self.server.listen(config.MAX)
        print("Connected")

    def run(self):
        self.main_thread = eventlet.spawn(self.accept_any)
        print("Spawned")
        self.main_thread.wait()

    """Those who are connected and not yet in any group"""
    def handle_idle(self, conn):
        print("handle_idle")
        #TODO:

    def accept_any(self):
        self.server.settimeout(config.TIMEOUT)
        while True:
            conn = None
            address = None
            while conn is None:
                try:
                    conn, address = self.server.accept()
                except socket.timeout as t:
                    eventlet.sleep(config.TIMEOUT)
                    # conn, address = server.accept()
                    # handle(conn)
            print("Accepted" + str(address))
            eventlet.spawn_n(self.handle_idle, conn)


# def handle(conn):
#     while True:
#         p = Pmd()
#         print("Receive")
#         msg = p.read_msg(conn)
#         print("Reply" + msg)
#         p = Pmd("You said " + msg)
#         p.send_msg(conn)


# g = Group(8848)


# def accept_any(server):
#     while True:
#         conn = None
#         while conn is None:
#             try:
#                 conn, address = server.accept()
#             except socket.timeout as t:
#                 eventlet.sleep(0.5)
#             # conn, address = server.accept()
#
#             # handle(conn)
#         print("Accepted")
#         # eventlet.spawn_n(handle, conn)
#         eventlet.spawn_n(g.add_conn, conn)
#
#
#
# pool = eventlet.GreenPool(10000)

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
