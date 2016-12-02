# import eventlet
# import socket
# from network.Group import Group
# from multiprocessing.pool import Pool
from struct import Struct
from PIL import Image
import base64

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
    img.show()

    Image.frombytes()
if __name__ == "__main__":
    # p = Pool(2)
    # gp = eventlet.GreenPool(3)
    # p.apply(pool_wait_all, (gp, ))

    # A = [1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    # B = [1,1,0,0,0,1,1]
    # a, b= devide(A, B)
    # print(a,b)
    save_img(serialize_img("network/a.png"), "network/b.png")
