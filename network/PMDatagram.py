import json

import network.config as config
import network.connect as connect
from network.util import *



class PMDatagram:
    def __init__(self, msg=None):
        self.msg_len = None
        self.msg = msg
        self.state = None   # TODO:
        self.json_decoder = json.JSONEncoder()
        self.json_decoder.item_separator = ","
        self.json_decoder.key_separator = ":"
        self.json_decoder.allow_nan = True

    @staticmethod
    @exception_log
    def parse_len(byte_msg):
        try:
            msg_len = int.from_bytes(byte_msg[: config.HEADER_LEN], config.ENDIAN)
        except ValueError as ve:
            raise Exception("Invalid length header")    # TODO: use other exception
        return msg_len

    """most function receive msg as str not bytes"""
    @exception_log
    def read_msg(self, conn):
        byte_len = connect.read_conn(conn, config.HEADER_LEN)
        self.msg_len = self.parse_len(byte_len)
        self.msg = str(connect.read_conn(conn, self.msg_len), "utf-8")
        return self.msg

    @exception_log
    def send_msg(self, conn):
        byte_msg = len(self.msg).to_bytes(config.HEADER_LEN, config.ENDIAN) + bytes(self.msg, "utf-8")
        connect.write_conn(conn, byte_msg)

    @exception_log
    def read_json(self, conn):
        return json.loads(self.read_msg(conn))

    @exception_log
    def send_json(self, conn, dict_data):
        msg = self.json_decoder.encode(dict_data)
        self.send_msg(msg)

    @exception_log
    def send_msg_all(self, conn):
        byte_msg = len(self.msg).to_bytes(config.HEADER_LEN, config.ENDIAN) + bytes(self.msg, "utf-8")
        conn.sendall(byte_msg)

    @exception_log
    def get_raw_msg(self):
        return self.msg

