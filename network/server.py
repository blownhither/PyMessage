import eventlet
import socket
from PIL import Image

import network.config as config
from network.PMDatagram import PMDatagram as Pmd


def handle(conn):
    while True:
        p = Pmd()
        print("Receive")
        msg = p.read_msg(conn)
        print("Reply")
        p = Pmd("You said " + msg)
        p.send_msg(conn)


def serialize_img(img_path):
    img = Image.open(img_path)
    w, h = img.size
    ratio = config.IMAGE_MAX_SOLUTION / (w * h)
    if ratio < 1:
        img.resize(w * ratio, h * ratio)
    return img.tobytes()


pool = eventlet.GreenPool(10000)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((config.HOST, config.PORT))
    server.listen(config.MAX)
    print("Connected")

    "asvuhadsuvhdsuohvo"

    while True:
        conn, address = server.accept()

        handle(conn)
        # pool.spawn_n(handle, [conn])
        print("spawned")
        # pool.spawn(handle, conn)

