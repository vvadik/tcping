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
                     3: [b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                         b"\x00\x00\x00\x00\x00\x00\x00\x00\x03\x01\x00\x00"
                         b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                         b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'"
                         b"\x11'\x12\x00\x00\x00\x01"],
                     4: [b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']}
        self.current_case = 0

    def settimeout(self, timeout):
        pass

    def sendto(self, pack, client):
        pass

    def recv(self, count):
        if self.case[self.current_case]:
            pack = self.case[self.current_case][0]
            del self.case[self.current_case][0]
            return pack
        return b''

    def poll(self, timeout):
        if self.current_case == 4:
            sleep(1.5)
        return self


class TestTcping(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.socket = Network()
        ip = '127.0.0.1'
        self.ping = Ping(ip, 10001, ip, 10002, self.socket, 1, 0, 2)

    def test_opened_port(self):
        self.socket.current_case = 1

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.PORT_OPEN)

    def test_closed_port(self):
        self.socket.current_case = 2

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.PORT_CLOSED)

    def test_host_unreachable(self):
        self.socket.current_case = 3

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.HOST_UNREACHABLE)

    def test_foreign_pack_plus_timeout(self):
        self.socket.current_case = 4

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.TIMEOUT)
