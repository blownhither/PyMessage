#!/usr/bin/env python
"""Document here"""

import eventlet
import socket
import multiprocessing as mtp
import random
from threading import Thread, Event, Lock
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

        # self.group_info = None  # one slot, fetch and clear
        # self.group_info_event = Event()

        # single slot, fetch and clear.
        # Most UI-client use interfaces serialized
        # currently used for transmitting GROUP_INFO, GROUP_MEMBERS... things other than message
        self.buffer = None
        self.buffer_type = None
        self.buffer_event = Event()
        self.buffer_lock = Lock()
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
                if l is None:
                    logging.warning("Corrupted RETURN_GROUPS frame without 'l' field")
                    continue
                self._put_buffer(l, pc.RETURN_GROUPS)
                print("put Group info : " + str(l))
                continue

            elif t == pc.RETURN_GROUP_MEMBERS:
                l = d.get(fd["l"])
                if l is None:
                    logging.warning("Corrupted RETURN_GROUP_MEMBERS frame without 'l' field")
                    continue
                self._put_buffer(l, pc.RETURN_GROUP_MEMBERS)
                print("Put Group members : " + str(l))
                continue

            print("Server: " + d)
            self.read_lock.acquire()
            self.read_queue.append(d)
            self.read_lock.release()

    def _put_buffer(self, buffer, buffer_type):
        if buffer is None:
            logging.warning("Trying to put None in buffer (type %d)\n" % buffer_type)
        self.buffer_lock.acquire()
        self.buffer = buffer
        self.buffer_type = pc.RETURN_GROUPS
        logging.info("put buffer " + str(buffer))
        self.buffer_lock.release()
        self.buffer_event.set()

    def _fetch_buffer(self, buffer_type):
        while True:
            if self.buffer is None or self.buffer_type != buffer_type:
                self.buffer_event.wait(config.TIMEOUT)
            else:
                break
        self.buffer_lock.acquire()
        if self.buffer_type != buffer_type:
            logging.error("Buffer type mismatch (%d, %d)" % (buffer_type, self.buffer_type))
            self.buffer_lock.release()
            return None         # yield at type failure
        l = self.buffer
        self.buffer = None
        self.buffer_type = None
        self.buffer_event.clear()
        self.buffer_lock.release()
        return l

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
        l = self._fetch_buffer(pc.RETURN_GROUPS)
        return l


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


