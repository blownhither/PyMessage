#!/usr/bin/env python

import socket

import config
import util


def read_msg(server):
    print("read")
    msg_len = server.recv(config.HEADER_LEN)
    print(msg_len)
    try:
        msg_len = int(msg_len)
    except Exception:
        msg_len = 32
    msg = server.recv(msg_len)
    return str(msg, 'utf-8')


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((config.HOST, config.PORT))
    print("Connected")
    while True:
        msg = input("Msg: ")
        server.send(bytes(msg, "utf-8"))
        ans = read_msg(server)
        print(ans)