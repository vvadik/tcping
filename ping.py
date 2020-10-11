#!/usr/bin/python3

import struct
import array
import socket
import time
from statistics import Stat


def chksum(packet):
    """
    This function I took from scapy's open source code
    """
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff


class Ping:
    def __init__(self, pack, socket, count, inf=False):
        self.pack = pack
        self.socket = socket
        self.count = count
        if inf:
            self.count = 0
        self.stat = Stat()
        self.timeout = socket.gettimeout()

    def start(self):
        i = 1
        while True:
            if self.count and i > self.count:
                break
            self.stat.add(*self.ping(i), self)
            i += 1
        self.stat.get()

    def ping(self, seq):
        self.socket.settimeout(self.timeout)
        tcppacket = self.build(seq)

        start_time = time.time()
        self.socket.sendto(tcppacket, (self.pack.dst_host, self.pack.dst_port))
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
                    return 'Port is open', resp_time
                return 'Port closed', resp_time
            new_timeout = self.timeout - resp_time
            if new_timeout < 0:
                return 'Timeout', 0
            self.socket.settimeout(new_timeout)
            continue

    def build(self, seq):
        package = struct.pack(
            '!HHIIBBHHH',
            self.pack.src_port,  # Source Port
            self.pack.dst_port,  # Destination Port
            seq,              # SEQ
            0,              # ACK
            5 << 4,         # Data Offset
            2,     # Flags
            1024,           # Window
            0,              # Checksum
            0               # Urgent pointer
        )

        pseudo_hdr = struct.pack(
            '!4s4sHH',
            socket.inet_aton(self.pack.src_host),
            socket.inet_aton(self.pack.dst_host),
            socket.IPPROTO_TCP,
            len(package)
        )

        checksum = chksum(pseudo_hdr + package)
        package = package[:16] + struct.pack('H', checksum) + package[18:]

        return package
