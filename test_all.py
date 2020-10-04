#!/usr/bin/python3

import unittest
import socket
from ping import Ping
from packet import Packet
from tcping import get_ip, set_args


class Test_setup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pack_to_google = Packet(get_ip(),
                                10001,
                                socket.gethostbyname('www.google.com'),
                                80)
        pack_to_me = Packet('127.0.0.1',
                            10002,
                            '127.0.0.1',
                            10003)
        socket.setdefaulttimeout(2)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.ping_google = Ping(pack_to_google, self.s, 1)
        self.ping_myself = Ping(pack_to_me, self.s, 1)

    # @classmethod
    # def tearDownClass(self):
    #     self.s.close()

    def test_ping(self):
        response, reasone, resp_time = self.ping_google.ping(seq=1)
        self.ping_google.stat.get()
        self.assertEqual(response, True)
        self.assertEqual(reasone, 'port is open')

    def test_tcping(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.bind(('', 10003))

        self.ping_myself.ping(seq=1)
        data = s.recv(1024)
        data = data[21:]
        pack = b"\x12'\x13\x00\x00\x00\x01\x00\x00" \
               b"\x00\x00P\x02\x04\x00_\xba\x00\x00"

        self.assertEqual(data, pack)
        s.close()
        self.s.close()

    def test_parcing_args(self):
        args = Args(None, 4, 2, '127.0.0.1', None, 'abc.com')
        port, count, waiting, ip, inf, dst = set_args(args)
        self.assertEqual(port, 80)
        self.assertEqual(inf, False)
        self.assertEqual(waiting, 2)


class Args:
    def __init__(self, port, count, waiting, ip, inf, website):
        self.port = port
        self.count = count
        self.waiting = waiting
        self.ip = ip
        self.inf = inf
        self.website = website
