#!/usr/bin/python3

import struct
import itertools
import array
import socket
import time
from statistics import Stat


def chksum(msg):
    # """
    # This function I took from scapy's open source code
    # """

    # s = 0
    # # loop taking 2 characters at a time
    # for i in range(0, len(msg), 2):
    #     # print(msg[i], type(msg[i]))
    #     w = (((msg[i])) << 8) + (((msg[i + 1])))
    #     s = s + w
    #
    # s = (s >> 16) + (s & 0xffff)
    # s = s + (s >> 16)
    # # complement and mask to 4 byte short
    # s = ~s & 0xffff
    # -----------------------
    # if len(msg) % 2 != 0:
    #     msg += b'\0'
    #
    # res = sum(array.array("H", msg))
    # res = (res >> 16) + (res & 0xffff)
    # res += res >> 16
    # res = ~res & 0xffff
    # ------------------------------
    s = 0
    n = len(msg) % 2
    for i in range(0, len(msg) - n, 2):
        s += (msg[i]) + ((msg[i + 1]) << 8)
        if n:
            s += (msg[i + 1])
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xffff

    # print(res, s)

    return s


class Ping:
    def __init__(self, src_host, src_port, dst_host, dst_port, socket, count):
        self.src_host = src_host
        self.src_port = src_port
        self.dst_host = dst_host
        self.dst_port = dst_port
        self.socket = socket
        self.count = count
        self.stat = Stat()
        self.timeout = socket.gettimeout()

    def start(self):
        counter = itertools.count(1)
        while self.count:
            self.stat.add(*self.ping(next(counter)),
                          self.dst_host, self.dst_port)
            self.count -= 1
        self.stat.get()

    def ping(self, seq):
        self.socket.settimeout(self.timeout)
        tcppacket = self.build(seq, 2)

        start_time = time.time()
        self.socket.sendto(tcppacket, (self.dst_host, self.dst_port))
        return self.parse_packages(start_time, seq)

    def parse_packages(self, start_time, seq):
        while True:
            try:
                data = self.socket.recv(16384)
            except socket.timeout:
                return 'Timeout', 0
            resp_time = time.time() - start_time
            answ = struct.unpack('!BBBBIIBB', data[20:34])
            if answ[1] == 3:
                return 'Host unreachable', 0
            if answ[5] == seq + 1:
                if answ[7] == 18:
                    # rst pack
                    self.socket.sendto(self.build(seq, 4),
                                       (self.dst_host, self.dst_port))
                    return 'Port is open', resp_time
                return 'Port closed', resp_time
            new_timeout = self.timeout - resp_time
            if new_timeout < 0:
                return 'Timeout', 0
            self.socket.settimeout(new_timeout)
            continue

    def build(self, seq, flags):
        package = struct.pack(
            '!HHIIBBHHH',
            self.src_port,  # Source Port
            self.dst_port,  # Destination Port
            seq,              # SEQ
            0,              # ACK
            5 << 4,         # Data Offset
            flags,     # Flags
            1024,           # Window
            0,              # Checksum
            0               # Urgent pointer
        )

        pseudo_hdr = struct.pack(
            '!4s4sHH',
            socket.inet_aton(self.src_host),
            socket.inet_aton(self.dst_host),
            socket.IPPROTO_TCP,
            len(package)
        )

        checksum = chksum(pseudo_hdr + package)
        package = package[:16] + struct.pack('H', checksum) + package[18:]

        return package
