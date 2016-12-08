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
            # dprint("read_conn_tuple: " + str(byte_msg, "utf-8"))
        except socket.timeout as e:
            eventlet.sleep(config.SLEEP)
        except ConnectionError as e:
            dprint(str(eventlet.getcurrent()) + " exit")
            try:
                eventlet.kill(eventlet.getcurrent())
            except Exception as e:   # if this not something spawned
                log_str = "Cannot kill thread " + str(e)
                logging.info(log_str)
                dprint(log_str)
                pass
    return byte_msg, addr


@exception_log
def read_conn(conn, length):
    byte_msg, addr = read_conn_tuple(conn, length)
    return byte_msg


@exception_log
def write_conn(conn, byte_msg):
    # conn.settimeout(config.TIMEOUT)
    try:
        # dprint("connect.write_conn : " + str(byte_msg))
        return conn.sendall(byte_msg)   # sendall ensures sending whole string despite buffer size
        # return conn.send(byte_msg)
    except ConnectionError as e:
        eventlet.kill(eventlet.getcurrent())
        raise e
    except OSError as e:
        print("OSError")
