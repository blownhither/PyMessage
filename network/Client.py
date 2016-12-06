#!/usr/bin/env python
"""Document here"""

import eventlet
import socket
import multiprocessing as mtp
import random
from threading import Thread, Event
import time

import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.PMDatagram import *
from network.util import *


"""Usage:
    client = Client(8848)
    client.start()

    # anytime
    client.put_msg(msg)
"""


class Client(Thread):
    def __init__(self, client_id):
        Thread.__init__(self)
        self.client_id = client_id
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((config.CLIENT_HOST, config.PORT))
        print("Connected")
        self.send_queue = []
        self.read_queue = []
        self.send_lock = mtp.Lock()
        self.read_lock = mtp.Lock()
        self.group_info = None  # one slot, fetch and clear
        self.group_info_event = Event()

        # self.thread_pool = eventlet.GreenPool(2)
        # self.thread_pool.spawn(self._read_routine)
        # self.thread_pool.spawn(self._send_routine)

        # self.read_thread = eventlet.spawn(self._read_routine)
        # self.send_thread = eventlet.spawn(self._send_routine)

    """override Thread.run"""
    def run(self):
        read_thread = eventlet.spawn(self._read_routine)
        send_thread = eventlet.spawn(self._send_routine)
        send_thread.wait()
        read_thread.wait()
        # self.thread_pool.waitall()

    def _read_routine(self):
        while True:
            p = Pmd()
            print("Reading.. ")
            d = p.read_json(self.server)
            if d is None:
                raise PMEmptyDataException()

            # TODO: design

            t = d.get(fd[0])
            if t is None:
                continue
            if t == pc.RETURN_GROUPS:
                l = d.get(fd["l"])
                self.group_info = l
                print("Group info : " + str(l))
                self.group_info_event.set()
                continue

            print("Server: " + d)
            self.read_lock.acquire()
            self.read_queue.append(d)
            self.read_lock.release()

    def _send_routine(self):
        while True:
            while len(self.send_queue) == 0:
                eventlet.sleep(config.SLEEP)
            print("%d Left" % len(self.send_queue))
            msg = self.send_queue.pop(0)
            p = Pmd(msg)
            p.send_raw_msg(self.server)
            print("Sent")

    def put_msg(self, msg):
        self.send_lock.acquire()
        self.send_queue.append(msg)
        self.send_lock.release()

    def read_msg(self):
        self.read_lock.acquire()
        ret = self.read_queue.pop(0)
        self.read_lock.release()
        return ret

    def get_groups(self):
        p = Pmd()
        p.require_groups(self.server)
        while True:
            if self.group_info is None:
                self.group_info_event.wait(timeout=config.TIMEOUT)
            else:
                l = self.group_info
                self.group_info = None
                return l
        # msg = p.read_msg(self.server)
        # flag = True
        # while flag:
        #     try:
        #         p.parse_groups(msg)
        #         flag = False
        #     except PMTypeException as e:
        #         flag = True
        #         self.read_queue.append(msg)






if __name__ == "__main__":
    client = Client(8848)
    client.start()

    print(client.get_groups())
    print(client.get_groups())
    # client.get_groups()
    # client.get_groups()
    #
    # while True:
        # client.put_msg(str(random.randint(1, 1000)))


    # eventlet.spawn(client.start)
    # eventlet.spawn(main)


