import eventlet
import socket
import random
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
        self._id_pool = {}       # [user_id] => conn
        # self._idle_pool = {}
        self._main_thread = None

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.settimeout(0.5)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((config.HOST, config.PORT))
        self._server.listen(config.MAX)
        dprint("Connected")

    def run(self):
        self._main_thread = eventlet.spawn(self._accept_any)
        self._main_thread.wait()

    """Thread routines"""
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
            dprint("Accepted" + str(address))
            eventlet.spawn_n(self._handle_any, conn)

    """Those who are connected and not yet in any group"""
    def _handle_any(self, conn):
        p = Pmd()
        dprint("_handle_idle")
        while True:
            d = p.read_json(conn)
            dprint(d)
            if d is None:       # TODO: must be error and need exit ?
                log_str = "Conn %s closing, threads exit " % str(conn)
                dprint(log_str)
                conn.close()
                logging.error(log_str)
                eventlet.kill(eventlet.getcurrent())

            t = d.get(fd[0])
            if t is not None:
                if t == pc.GET_GROUPS:
                    p.send_groups(conn, self.get_group_info())
                    continue

                elif t == pc.CREATE_GROUP:
                    group_name = d.get(fd["x"])
                    if group_name is None:
                        log_str = "Corrupted CREATE_GROUP frame missing group_name"
                        logging.error(log_str)
                        dprint(log_str)
                    group_id = self._add_group(name=group_name)
                    p.confirm_add_group(conn, group_id, group_name)
                    continue

                elif t == pc.GET_GROUP_MEMBERS:
                    group_id = d.get(fd["g"])
                    if group_id is not None:
                        l = self.get_group_members(group_id)
                        if l is not None:
                            p.send_group_members(conn, group_id, l)
                    continue

                elif t == pc.JOIN_GROUP:
                    group_id = d.get(fd["g"])
                    user_id = d.get(fd["u"])
                    alias = d.get(fd["x"])
                    success = self.join_group(conn, group_id, user_id, alias)
                    if success:
                        log_str = "%d(%s) joined group %d" % (user_id, alias, group_id)
                    else:
                        log_str = "%d(%s) request for joining group %d rejected " % (user_id, alias, group_id)
                        group_id = -1
                        alias = ""
                    logging.info(log_str)
                    dprint(log_str)
                    p.confirm_join_group(conn, group_id, alias)
                    continue

                elif t == pc.CLIENT_SEND_MSG:
                    self._broadcast(conn, d)
                    print(d["u"])
                    # TODO: deal with ret
                    continue

                elif t == pc.REQUEST_ID:
                    user_id = self.assign_user_id(conn)
                    print("Assigned User ID " + str(user_id))
                    continue

                else:
                    log_str = " Unrecognized frame type " + str(t)
                    dprint(log_str)
                    logging.warning(log_str)
                    continue

    """ with parameter check, return False on failure """
    def join_group(self, conn, group_id, user_id, alias=None):
        group = self._group_pool.get(group_id)
        if group_id is None or group is None:
            warning_str = str(conn) + "Attempt to join invalid group " + str(group_id)
            dprint(warning_str)
            logging.warning(warning_str)
            return False
        return group.add_user(conn=conn, user_id=user_id, user_name=alias)

    def add_group(self, group_id):
        self._add_group(group_id)

    # Throws Exception
    def _add_group(self, group_id=None, name="Temporary Group", desc=""):
        if group_id is None:
            while True:
                group_id = random.randint(config.GROUP_ID_MIN, config.GROUP_ID_MAX)
                if self._group_pool.get(group_id) is None:
                    break
        elif self._group_pool.get(group_id) is not None:
            warning_str = "Re-create group_id / groupId collision on " + str(group_id)
            dprint(warning_str)
            logging.warning(warning_str)
            return False
        g = Group(group_id=group_id, desc=desc, name=name)
        self._group_pool[group_id] = g
        return group_id

    def _broadcast(self, conn, datagram):
        group_id = datagram.get(fd["g"])
        g = self._group_pool.get(group_id)
        if g is None:
            log_str = "Broadcast to invalid group " + str(group_id)
            dprint(log_str)
            logging.error(log_str)
            return
        datagram[fd[0]] = pc.SERVER_SEND_MSG
        g.add_msg(conn, datagram)

    """ Format [(group_id, name, n_members), ... ]"""
    def get_group_info(self):
        return [x.group_info() for x in self._group_pool.values()]

    """ Format [(user_id, user_name, user_desc), ... ]"""
    def get_group_members(self, group_id):
        g = self._group_pool.get(int(group_id))
        if g is None:
            warning_str = "Get users from invalid group ID " + str(group_id)
            dprint(warning_str)
            logging.warning(warning_str)
            return None
        return g.user_list()

    def assign_user_id(self, conn):
        user_id = None
        while True:
            user_id = random.randint(config.ID_MIN, config.ID_MAX)
            if user_id not in self._id_pool.keys():
                break
        self._id_pool[user_id] = conn
        p = Pmd()
        p.return_user_id(conn, user_id)
        return user_id


if __name__ == "__main__":
    s = Server()
    s.start()
    s.add_group(8848)
    s.add_group(7737)
    s.add_group(6626)
    print(s.get_group_info())



