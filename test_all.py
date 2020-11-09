#!/usr/bin/python3

import unittest
from time import sleep
from ping import Ping, Answer


class Network:
    def __init__(self):
        self.case = {1: [b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00"
                         b"\x00\x00\x01\x00\x00\x00\x02P\x12\x04\x00\x00\x00"
                         b"\x00\x00"],
                     2: [b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00"
                         b"\x00\x00\x01\x00\x00\x00\x02P\x14\x04\x00\x00\x00"
                         b"\x00\x00"],
                     3: [b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00\x00"
                         b"\x00\x01\x00\x00\x00\x03P\x12\x04\x00\x00\x00\x00"
                         b"\x00",
                         b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00\x00"
                         b"\x00\x01\x00\x00\x00\x03P\x12\x04\x00\x00\x00\x00\
                         x00"]}
        self.current_case = 0

    def settimeout(self, timeout):
        pass

    def sendto(self, pack, client):
        pass

    def recv(self, count):
        if self.current_case == 3:
            sleep(2)
        pack = self.case[self.current_case][0]
        del(self.case[self.current_case][0])
        return pack


class Test_setup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.socket = Network()
        self.socket.settimeout(2)
        ip = '127.0.0.7'
        self.ping = Ping(ip, 10001, ip, 10002, self.socket, 1, 0, 2)

    def test_opened_port(self):
        self.socket.current_case = 1

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.port_open)

    def test_closed_port(self):
        self.socket.current_case = 2

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.port_closed)

    def test_timeout(self):  # + случай когда нам не наши пакеты приходят
        self.socket.current_case = 3

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.timeout)
