#!/usr/bin/python3

import unittest
import socket
from ping import Ping
from packet import Packet
from tcping import get_ip


class Test_setup(unittest.TestCase):
    def setup_class(self):
        pack_to_google = Packet(get_ip(),
                           10001,
                           socket.gethostbyname('www.google.com'),
                           80)
        pack_to_me = Packet('127.0.0.1',
                           10002,
                           '127.0.0.1',
                           10003)
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.ping_google = Ping(pack_to_google, s, 1)
        self.ping_myself = Ping(pack_to_me, s, 1)

    def test_ping(self):
        response, reasone, resp_time = self.ping_google.ping()
        self.ping_google.stat.get()
        self.assertEqual(response, True)
        self.assertEqual(reasone, 'port is open')

    def test_tcping(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.bind(('', 10003))

        self.ping_myself.ping()
        data = s.recv(1024)
        data = data[21:]
        pack = b"\x12'\x13\x00\x00\xa5h\x00\x00\x00\x00P" \
               b"\x02\x04\x00\xbaR\x00\x00"

        self.assertEqual(data, pack)
