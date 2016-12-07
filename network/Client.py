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



class Client(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.user_id = None
        self.user_id_event = Event()
        self.server = None
        self._connect()
        self.send_queue = []    # [(msg, group_id), ...]
        self.read_queue = []    # [{msg=, groupId=, userId=, time=}]
        self.send_lock = Lock()
        self.read_lock = Lock()
        self.read_event = Event()

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
        self._request_user_id()


    def __del__(self):
        self.server.close()

    def close(self):
        self.server.close()

    """override Thread.run"""
    def run(self):
        read_thread = eventlet.spawn(self._read_routine)
        send_thread = eventlet.spawn(self._send_routine)
        send_thread.wait()
        read_thread.wait()
        # self.thread_pool.waitall()

    """Network connections """
    def _connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((config.CLIENT_HOST, config.PORT))
        print("Connected")

    def _reconnect(self):
        if self.server is not None:
            self.server.close()
            self.server = None
        while self.server is None:
            try:
                self._connect()  # try to reconnect
            except Exception as e:
                log_str = str(e) + "\nUnable to reach server"
                dprint(log_str)
                logging.error(log_str)
                self.server = None
                time.sleep(config.LONG_TIMEOUT)

    """Must-do routines"""
    def _request_user_id(self):
        dprint("Requesting user id")
        p = Pmd()
        p.request_user_id(self.server)

    """Thread rountines"""
    def _read_routine(self):
        while True:
            p = Pmd()
            # dprint("Reading.. ")
            d = p.read_json(self.server)
            if d is None:
                # raise PMEmptyDataException()
                log_str = "Conn %s closing, threads exit " % str(self.server)
                dprint(log_str)
                self._reconnect()
                continue

            t = d.get(fd[0])
            if t is None:
                continue
            if t == pc.RETURN_GROUPS:
                l = d.get(fd["l"])
                if l is None:
                    logging.warning("Corrupted RETURN_GROUPS frame without 'l' field")
                    continue
                self._put_buffer(l, pc.RETURN_GROUPS)
                dprint("put Group info : " + str(l))
                continue

            elif t == pc.RETURN_GROUP_MEMBERS:
                l = d.get(fd["l"])
                if l is None:
                    logging.warning("Corrupted RETURN_GROUP_MEMBERS frame without 'l' field")
                    continue
                self._put_buffer(l, pc.RETURN_GROUP_MEMBERS)
                dprint("Put Group members : " + str(l))
                continue

            elif t == pc.CONFIRM_JOIN_GROUP:
                group_id = d.get(fd["g"])
                self._put_buffer(group_id, pc.CONFIRM_JOIN_GROUP)
                dprint("Confirm joined group " + str(group_id))
                continue

            elif t == pc.SERVER_SEND_MSG:
                self._add_read_queue(d)
                # dprint("get message")

            elif t == pc.RETURN_ID:
                id = d.get(fd["u"])
                if id is None:
                    log_str = "Corrupted RETURN_ID frame, missing UserID"
                    logging.error(log_str)
                    dprint(log_str)
                    continue
                if self.user_id is not None:
                    log_str = "User ID Re-assignment %d->%d" % (self.user_id, id)
                    logging.warning(log_str)
                    dprint(log_str)
                self.user_id = id
                self.user_id_event.set()

            elif t == pc.CONFIRM_CREATE_GROUP:
                group_name = d.get(fd["x"])
                group_id = d.get(fd["g"])
                if group_id is None or group_name is None:
                    log_str = "Corrupted CONFIRM_CREATE_GROUP frame, missing GROUP_ID or _NAME"
                    logging.error(log_str)
                    dprint(log_str)
                self._put_buffer((group_id, group_name), pc.CONFIRM_CREATE_GROUP)

            else:
                log_str = "Unrecognized frame type"
                dprint(log_str)
                logging.error(log_str)
                continue

    def _send_routine(self):
        p = Pmd()
        while True:
            while len(self.send_queue) == 0:
                eventlet.sleep(config.SLEEP)
            # dprint("%d Left" % len(self.send_queue))
            self.send_lock.acquire()
            if len(self.send_queue) == 0:
                self.send_lock.release()
                continue
            msg, group_id = self.send_queue.pop(0)
            self.send_lock.release()
            p.send_msg(self.server, group_id, self.user_id, "", msg)
            dprint("\t\t\t\tSent msg : " + msg)

    """Buffer routines"""
    def _put_buffer(self, buffer, buffer_type):
        if buffer is None:
            logging.warning("Trying to put None in buffer (type %d)\n" % buffer_type)
        self.buffer_lock.acquire()
        self.buffer = buffer
        self.buffer_type = buffer_type
        logging.info("put buffer (type=%d)%s" % (buffer_type, str(buffer)))
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
        dprint("Fetched " + str(l))
        return l

    def get_user_id(self):
        self.user_id_event.wait(config.LONG_TIMEOUT)
        while self.user_id is None:
            self._request_user_id()
            self.user_id_event.wait(config.LONG_TIMEOUT)    # TODO: ?!
        self.user_id_event.clear()
        return self.user_id

    def put_msg(self, msg, group_id):
        if self.user_id is None:
            self.get_user_id()
        self.send_lock.acquire()
        self.send_queue.append((str(msg), group_id))
        self.send_lock.release()

    def _add_read_queue(self, datagram):
        self.read_lock.acquire()
        d = {
            "msg": datagram[fd["x"]],
            "groupId": datagram[fd["g"]],
            "userId": datagram[fd["u"]],
            "userName": datagram[fd["n"]],
            "time": datagram[fd["Time"]],
        }
        self.read_queue.append(d)
        self.read_event.set()
        self.read_lock.release()

    def read_msg(self, blocking=True):
        if blocking is False:
            self.read_lock.acquire()
            if len(self.read_queue) > 0:
                ret = self.read_queue.copy()
                self.read_queue.clear()
            else:
                ret = None
            self.read_lock.release()
            return ret
        # use blocking
        while True:
            if len(self.read_queue) == 0:
                success = self.read_event.wait(config.TIMEOUT)
                continue
            else:
                self.read_lock.acquire()
                if len(self.read_queue) == 0:
                    self.read_lock.release()
                    continue
                # ret = self.read_queue.pop(0)
                ret = self.read_queue.copy()
                self.read_queue.clear()
                self.read_event.clear()
                self.read_lock.release()
                return ret

    def get_groups(self):
        p = Pmd()
        p.request_groups(self.server)
        l = self._fetch_buffer(pc.RETURN_GROUPS)
        return l

    def get_group_members(self, group_id):
        p = Pmd()
        p.request_group_members(self.server, group_id)
        l = self._fetch_buffer(pc.RETURN_GROUP_MEMBERS)
        return l

    def add_group(self, group_name):
        p = Pmd()
        p.request_add_group(self.server, self.user_id, group_name)
        group_id, group_name2 = self._fetch_buffer(pc.CONFIRM_CREATE_GROUP)
        if group_name != group_name2:
            log_str = "add_group: Group renamed arbitrarily %s->%s" % (group_name, group_name2)
            logging.warning(log_str)
            dprint(log_str)
        return group_id

    def join_group(self, group_id, alias=None):
        if self.user_id is None:
            self.get_user_id()
        p = Pmd()
        while True:
            p.request_join_group(self.server, group_id, self.user_id, alias)
            ret = self._fetch_buffer(pc.CONFIRM_JOIN_GROUP)
            if ret == group_id:     # if mismatch caused by another thread (shouldn't happen), please require again
                return True
            else:
                log_str = "Unmatched joining group %d feedback, unimplemented async? " % group_id
                dprint(log_str)
                logging.error(log_str)
                return False            # Temporary



if __name__ == "__main__":
    # r = random.randint(0, 1000)
    client = Client()
    client.start()
    print("This is " + str(client.get_user_id()))
    # print(client.join_group(8848, "mzy2"))  # Rename

    group_id = client.add_group("BILIBILI")
    print(client.get_groups())
    print(client.join_group(group_id, "mzy"))

    while True:
        msg = "Hello No." + str(random.randint(1000, 2000))
        client.put_msg(msg, group_id)
        ml = None
        while ml is None:
            ml = client.read_msg(blocking=False)
        for x in ml:
            print("%s(%s):\n\t%s" % (x["userName"], str(x["userId"]), str(x["msg"])))
        time.sleep(3)
    client.close()

    # eventlet.spawn(client.start)
    # eventlet.spawn(main)


