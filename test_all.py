#!/usr/bin/python3

import unittest
import struct
import socket
from ping import Ping


class Test_setup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pack_to_me = Package('127.0.0.1',
                             10002,
                             '127.0.0.1',
                             10003)
        socket.setdefaulttimeout(2)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_TCP)

        self.ping = Ping(pack_to_me, self.socket, 1)
        self.foreign_package = build_package(self.ping, 100, 101, 18)
        self.normal_package = build_package(self.ping, 1, 2, 18)

    def test_opened_port(self):
        s = socket.socket()
        s.bind(('', 10003))
        s.listen(1)

        self.socket.sendto(self.foreign_package, ('127.0.0.1', 10002))
        resp, time = self.ping.ping(seq=1)
        self.assertEqual(resp, 'Port is open')
        s.close()

    def test_closed_port(self):
        self.socket.sendto(self.foreign_package, ('127.0.0.1', 10000))
        resp, time = self.ping.ping(seq=1)
        self.assertEqual(resp, 'Port closed')
