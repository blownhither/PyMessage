import eventlet
import socket

def p(a):
    print(a)

if __name__ == "__main__":
    while True:
        th = eventlet.spawn(p, 12)
        th.wait()