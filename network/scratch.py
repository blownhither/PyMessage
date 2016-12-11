import eventlet
# import socket
# from network.Group import Group
# from multiprocessing.pool import Pool
from struct import Struct
from PIL import Image
import base64
from threading import Thread, Event, Lock
import time
import json
import asyncio
import sqlite3
import pyDes

#
# def pr(a):
#     print(a)
#
# def pr2():
#     print(2)
#
# def pool_wait_all(pool):
#     print("Threads start")
#     pool.waitall()
#
# class Test:
#     def __init__(self):
#         return

def sub(l1, l2):
    l = []
    for i in range(len(l2)):
        # print("%d %d" % (i, abs(l1[i] - l2[i])))
        l.append(abs(l1[i] - l2[i]))
    return l

def trim(l):
    while len(l) > 0 and l[0] == 0:
        l.pop(0)
    return l

def devide(l1, l2): # l1 / l2
    m = len(l2)
    ans = []
    # rem = trim(sub(l1[:m], l2))
    rem = []

    while len(l1) > 0:
        while len(l1) > 0 and len(rem) < m:
            ans.append(0)
            rem.append(l1.pop(0))
            print(ans)
        if len(rem) == m:
            ans.append(1)
            rem = trim(sub(rem, l2))
        else:
            return ans, rem
    return ans, rem


def serialize_img(img_path):
    # img = Image.open(img_path)
    # w, h = img.size
    # ratio = config.IMAGE_MAX_SOLUTION / (w * h)
    # if ratio < 1:
    #     img.resize(w * ratio, h * ratio)
    # i = Struct.pack(img)
    # return i
    # TODO: check image type
    f = open(img_path, "rb")
    byte_msg = f.read()
    return byte_msg

def save_img(byte_msg, path):
    f = open(path, "wb")
    f.write(byte_msg)

    i = Image.open(path)
    i.show()


def img_from_srial(byte_img):
    s = Struct().pack(byte_img)
    # img.show()


    Image.frombytes()


class MyThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.spawn_lock = Lock()

    def run(self):
        self.spawn_lock.acquire()
        t = eventlet.spawn(self.p)
        self.spawn_lock.release()
        t.wait()

    def p(self):
        while True:
            print("a")
            eventlet.sleep(1)


class T():
    pub = []

    def __init__(self):
        T.pub.append(3)
        print(str(T.pub))


des = pyDes.des("ZZSBETJD", pad=" ")


def read_raw_msg(des_all):
    global  des
    des_len = des_all[: 8]
    byte_len = des.decrypt(des_len)
    print("byte_len : " + str(byte_len))
    msg_len = int.from_bytes(byte_len, 'big')
    print("msg_len : " + str(msg_len))

    des_msg = des_all[8: ]
    if len(des_msg) != msg_len:
        print("!!!!!!")

    byte_msg = des.decrypt(des_msg)
    msg = str(byte_msg, "utf-8")
    print("read_raw_msg : " + msg)
    return msg


def send_raw_msg(msg):
    global des
    des_msg = des.encrypt(bytes(msg, "utf-8"))
    byte_header = len(des_msg).to_bytes(8, "big")
    des_header = des.encrypt(byte_header)
    print("send_raw_msg: %s->%s" % (msg, des_header + des_msg))
    return des_header + des_msg

if __name__ == "__main__":
    # while True:
    #     raw = send_raw_msg("Hello")
    #     ret = read_raw_msg(raw)
    #     print(ret)

    t = MyThread()
    t.start()
    t1 = MyThread()
    t1.start()
    # eventlet.sleep(0)
    # t.join()
    # t1.join()

    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.settimeout(0.5)
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # server.bind((config.HOST, config.PORT))
    # server.listen(config.MAX)
    # print("Connected")
    # main_thread = eventlet.spawn(accept_any, server)
    # main_thread.wait()



    # db = sqlite3.connect("test.db")
    # db.execute("create table test (a int primary key, b int);")
    # db.execute("insert into test values (3, 5);")
    # cursor = db.execute("select * from test;")
    # cursor.fetchall()
