import eventlet
import socket
from network.Group import Group
from multiprocessing.pool import Pool


def pr(a):
    print(a)

def pr2():
    print(2)

def pool_wait_all(pool):
    print("Threads start")
    pool.waitall()

class Test:
    def __init__(self):
        return

if __name__ == "__main__":
    p = Pool(2)
    gp = eventlet.GreenPool(3)
    p.apply(pool_wait_all, (gp, ))