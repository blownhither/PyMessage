#!/usr/bin/env python
"""Document here"""

import eventlet
import socket
import multiprocessing as mtp
import random

import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.util import *


def pool_wait_all(pool):
    print("Threads start")
    pool.waitall()


class Client:
    def __init__(self, client_id):
        # TODO: verify client ID
        self.client_id = client_id
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((config.HOST, config.PORT))
        print("Connected")
        # self.thread_pool = eventlet.GreenPool(2)
        self.send_queue = []
        self.read_queue = []
        self.read_thread = eventlet.spawn(self._read_routine)
        # self.read_thread = self.thread_pool.spawn(self._read_routine)
        self.send_thread = eventlet.spawn(self._send_routine)
        # self.send_thread = self.thread_pool.spawn(self._send_routine)
        # p = Pool(processes=2)
        # p.apply_async(pool_wait_all, (self.thread_pool,))

    def _read_routine(self):
        while True:
            p = Pmd()
            print("Reading.. ")
            msg = p.read_msg(self.server)
            # TODO:
            print("Server: " + msg)
            self.read_queue.append(msg)

    def read_routine(self):
        self._read_routine()

    def _send_routine(self):
        while True:
            while len(self.send_queue) == 0:
                eventlet.sleep(config.SLEEP)
            print("%d Left" % len(self.send_queue))
            msg = self.send_queue.pop(0)
            p = Pmd(msg)
            p.send_msg(self.server)
            print("Sent")

    def put_msg(self, msg):
        self.send_queue.append(msg)


# @exception_log
# def read_msg(server):
#     p = Pmd(server=server)
#     return p.get_raw_msg()

#
# def main():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.connect((config.HOST, config.PORT))
#     print("Connected")
#     while True:
#         msg = input("Msg: ")
#         p = Pmd(msg)
#         p.send_msg(server)
#         ans = p.read_msg(server)
#         print("Server: " + ans)


if __name__ == "__main__":
    client = Client(8848)

    while True:

        client.put_msg(str(random.randint(1, 1000)))
        eventlet.sleep(2)

    # eventlet.spawn(client.start)
    # eventlet.spawn(main)


