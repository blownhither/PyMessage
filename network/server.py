import eventlet
import socket
import config


def prepare_msg(msg):
    msg = str(msg, "utf-8")
    ret = "%016d" % len(msg)
    ret += msg
    return bytes(ret, "utf-8")


def handle(conn):
    while True:
        c = conn.recv(1)
        print("handle")
        conn.sendall(prepare_msg(c))

pool = eventlet.GreenPool(10000)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((config.HOST, config.PORT))
    server.listen(config.MAX)
    print("Connected")

    while True:
        conn, address = server.accept()
        handle(conn)
        # pool.spawn_n(handle, conn)