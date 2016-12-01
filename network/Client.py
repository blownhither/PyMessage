#!/usr/bin/env python
"""Document here"""

import socket

import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.util import *


class Client:
    pass


@exception_log
def read_msg(server):
    p = Pmd(server=server)
    return p.get_raw_msg()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((config.HOST, config.PORT))
    print("Connected")
    while True:
        msg = input("Msg: ")
        p = Pmd(msg)
        p.send_msg(server)
        ans = p.read_msg(server)
        print("Server: " + ans)


if __name__ == "__main__":
    main()