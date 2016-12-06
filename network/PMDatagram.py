import json

import pub_config as pc
from pub_config import FIELDS as fd
import network.config as config
import network.connect as connect
from network.util import *


class PMDatagram:

    def __init__(self, msg=None, data=None):
        self.msg_len = None
        self.msg = msg
        self.data = data
        self.state = None   # TODO:
        self.json_decoder = json.JSONEncoder()
        self.json_decoder.item_separator = ","
        self.json_decoder.key_separator = ":"
        self.json_decoder.allow_nan = True

    """ Methods operating on raw data and JSON Datagram
        most interfaces receive msg as str not bytes unless specified
    """

    @staticmethod
    @exception_log
    def parse_len(byte_msg):
        try:
            msg_len = int.from_bytes(byte_msg[: config.HEADER_LEN], config.ENDIAN)
        except ValueError as ve:
            raise Exception("Invalid length header")    # TODO: use other exception
        return msg_len

    @exception_log
    def read_raw_msg(self, conn):
        byte_len = connect.read_conn(conn, config.HEADER_LEN)
        self.msg_len = self.parse_len(byte_len)
        self.msg = str(connect.read_conn(conn, self.msg_len), "utf-8")
        print("read_raw_msg : " + self.msg)
        return self.msg

    @exception_log
    def send_raw_msg(self, conn, msg=None):
        if msg is None:
            msg = self.msg
        byte_msg = len(msg).to_bytes(config.HEADER_LEN, config.ENDIAN) + bytes(msg, "utf-8")
        connect.write_conn(conn, byte_msg)
        print("send_raw_msg : %s\n\t%s" % (msg, byte_msg))

    @exception_log
    def read_json(self, conn):
        raw_msg = self.read_raw_msg(conn)
        print("raw: " + raw_msg)
        try:
            d = json.loads(raw_msg)
        except json.JSONDecodeError as e:
            raise PMJSONException()
        print("dict: " + str(d))
        return d

    @exception_log
    def send_json(self, conn, dict_data=None):
        if dict_data is None:
            dict_data = self.data
        msg = self.json_decoder.encode(dict_data)
        self.send_raw_msg(conn, msg)
        print("json str : " + msg)

    @exception_log
    def send_msg_all(self, conn):
        byte_msg = len(self.msg).to_bytes(config.HEADER_LEN, config.ENDIAN) + bytes(self.msg, "utf-8")
        conn.sendall(byte_msg)

    @exception_log
    def get_raw_msg(self):
        return self.msg

    """
        Methods about groups
        Refer to pub_config to read about groups data specifications
        [(group_id, name, n_members), ]
    """
    @exception_log
    def require_groups(self, conn):
        d = {
            fd[0]: pc.GET_GROUPS,
            fd[1]: -1,
            fd[2]: -1,
        }
        self.send_json(conn, d)

    @exception_log
    def send_groups(self, conn, tuple_list):
        d = {
            fd[0]: pc.RETURN_GROUPS,
            fd[1]: -1,
            fd[2]: -1,
            fd["l"]: tuple_list,
        }
        self.send_json(conn, d)

    @exception_log
    def parse_groups(self, d):
        if d[fd[0]] != pc.RETURN_GROUPS:
            raise PMTypeException()
        l = d.get(fd["l"])
        if l is None:
            raise PMDataException()
        return l

    """ Methods about group members
        format [(user_id, user_name, user_desc), ... ]
    """

    @exception_log
    def require_group_members(self, conn, group_id):
        d = {
            fd[0]: pc.GET_GROUP_MEMBERS,
            fd[1]: group_id,
            fd[2]: -1,
        }
        self.send_json(conn, d)

    @exception_log
    def send_group_members(self, conn, group_id, tuple_list):
        d = {
            fd[0]: pc.RETURN_GROUP_MEMBERS,
            fd[1]: group_id,
            fd[2]: -1,
            fd["l"]: tuple_list
        }
        self.send_json(conn, d)

    @exception_log
    def parse_group_members(self, d):
        if d[fd[0]] != pc.RETURN_GROUP_MEMBERS:
            raise PMTypeException()
        l = d.get(fd["l"])
        if l is None:
            raise PMDataException()
        return l

    """ Methods about joining groups
    """
    @exception_log
    def require_join_group(self, conn, group_id, user_id, alias=None):
        d = {
            fd[0]: pc.JOIN_GROUP,
            fd[1]: group_id,
            fd[2]: -1,
            fd["u"]: user_id,
            fd["x"]: alias
        }
        self.send_json(conn, d)

    @exception_log
    def confirm_join_group(self, conn, group_id, alias):
        d = {
            fd[0]: pc.CONFIRM_JOIN_GROUP,
            fd[1]: group_id,
            fd[2]: -1,
            fd["x"]: alias
        }
        self.send_json(conn, d)


class PMTypeException(Exception):
    pass


class PMDataException(Exception):
    pass


class PMEmptyDataException(Exception):
    pass


class PMJSONException(Exception):
    pass
