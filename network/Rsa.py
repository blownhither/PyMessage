# -*- coding: utf-8 -*-

import rsa
import string
import random

class Rsa:
    def __init__(self):
        self._pub = None
        self._priv = None
        try:
            with open("network/pub.txt", "rb") as f:
                self._pub = rsa.PublicKey.load_pkcs1(f.read(), 'DER')
        except IOError as e:
            pass
        try:
            with open("network/priv.txt", "rb") as f:
                self._priv = rsa.PrivateKey.load_pkcs1(f.read(), 'DER')
        except IOError as e:
            pass

    @staticmethod
    def generate():
        (pub, priv) = rsa.newkeys(256)
        with open("network/pub.txt", "wb") as f:
            f.write(pub.save_pkcs1('DER'))
        with open("network/priv.txt", "wb") as f:
            f.write(priv.save_pkcs1('DER'))

    def encrypt(self, msg):
        return rsa.encrypt(msg, self._pub)

    def decrypt(self, msg):
        return rsa.decrypt(msg, self._priv)

    @staticmethod
    def rand_des_key():
        return ''.join([random.choice(string.ascii_letters) for i in range(8)])