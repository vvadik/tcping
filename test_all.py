#!/usr/bin/python3

import unittest
import array
import struct
import socket
from ping import Ping


#
# def chksum(packet):
#     """
#     This function I took from scapy's open source code
#     """
#     if len(packet) % 2 != 0:
#         packet += b'\0'
#
#     res = sum(array.array("H", packet))
#     res = (res >> 16) + (res & 0xffff)
#     res += res >> 16
#
#     return (~res) & 0xffff


# def build_package(ping, seq, ack, flags):
#     package = struct.pack(
#         '!HHIIBBHHH',
#         ping.pack.src_port,  # Source Port
#         ping.pack.dst_port,  # Destination Port
#         seq,  # SEQ
#         ack,  # ACK
#         5 << 4,  # Data Offset
#         flags,  # Flags
#         1024,  # Window
#         0,  # Checksum
#         0  # Urgent pointer
#     )
#
#     pseudo_hdr = struct.pack(
#         '!4s4sHH',
#         socket.inet_aton(ping.pack.src_host),
#         socket.inet_aton(ping.pack.dst_host),
#         socket.IPPROTO_TCP,
#         len(package)
#     )
#
#     checksum = chksum(pseudo_hdr + package)
#     package = package[:16] + struct.pack('H', checksum) + package[18:]
#     return package


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
