import eventlet
import socket
from PIL import Image

import network.config as config
from network.PMDatagram import PMDatagram as Pmd
from network.Group import Group


def handle(conn):
    while True:
        p = Pmd()
        print("Receive")
        msg = p.read_msg(conn)
        print("Reply" + msg)
        p = Pmd("You said " + msg)
        p.send_msg(conn)


def serialize_img(img_path):
    img = Image.open(img_path)
    w, h = img.size
    ratio = config.IMAGE_MAX_SOLUTION / (w * h)
    if ratio < 1:
        img.resize(w * ratio, h * ratio)
    return img.tobytes()

g = Group(8848)

def accept_any(server):
    while True:
        conn = None
        while conn is None:
            try:
                conn, address = server.accept()
            except socket.timeout as t:
                eventlet.sleep(0.5)
            # conn, address = server.accept()

            # handle(conn)
        print("Accepted")
        # eventlet.spawn_n(handle, conn)
        eventlet.spawn_n(g.add_conn, conn)



pool = eventlet.GreenPool(10000)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(0.5)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((config.HOST, config.PORT))
    server.listen(config.MAX)
    print("Connected")
    main_thread = eventlet.spawn(accept_any, server)
    main_thread.wait()
        # pool.spawn(handle, conn)

