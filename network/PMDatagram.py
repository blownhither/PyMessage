import network.config as config
from network.util import *


class PMDatagram:
    def __init__(self, msg=None):
        self.msg_len = None
        self.msg = msg
        self.addr = None
        self.state = None   # TODO:

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
        byte_len, self.addr = conn.recvfrom(config.HEADER_LEN)
        self.msg_len = self.parse_len(byte_len)
        self.msg = str(conn.recv(self.msg_len), "utf-8")
        return self.msg

    @exception_log
    def send_msg(self, conn):
        byte_msg = len(self.msg).to_bytes(config.HEADER_LEN, config.ENDIAN) + bytes(self.msg, "utf-8")
        conn.send(byte_msg)

    @exception_log
    def send_msg_all(self, conn):
        byte_msg = len(self.msg).to_bytes(config.HEADER_LEN, config.ENDIAN) + bytes(self.msg, "utf-8")
        conn.sendall(byte_msg)

    @exception_log
    def get_raw_msg(self):
        return self.msg

