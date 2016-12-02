import eventlet
import socket

import network.config as config
from network.util import *

"""These functions should be called with threading, and they will sleep when blocked"""
"""Now connect functions kill the thread when conn broken, consider reset"""
@exception_log
def read_conn_tuple(conn, length):
    conn.settimeout(config.TIMEOUT)
    addr = None
    byte_msg = None
    while byte_msg is None:
        byte_msg = None
        try:
            byte_msg, addr = conn.recvfrom(length)
        except socket.timeout as e:
            eventlet.sleep(config.SLEEP)
        except ConnectionError as e:
            eventlet.kill(eventlet.getcurrent())
    return byte_msg, addr


@exception_log
def read_conn(conn, length):
    byte_msg, addr = read_conn_tuple(conn, length)
    return byte_msg


@exception_log
def write_conn(conn, byte_msg):
    conn.settimeout(config.TIMEOUT)
    try:
        return conn.send(byte_msg)
    except ConnectionError as e:
        eventlet.kill(eventlet.getcurrent())
        raise e

