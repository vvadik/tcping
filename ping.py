#!/usr/bin/python3

import struct
import itertools
import socket
import time
import enum
from statistics import Stat, print_stat


def chksum(msg):
    sum_ = 0
    n = len(msg) % 2
    for i in range(0, len(msg) - n, 2):
        sum_ += (msg[i]) + ((msg[i + 1]) << 8)
        if n:
            sum_ += (msg[i + 1])
    while sum_ >> 16:
        sum_ = (sum_ & 0xFFFF) + (sum_ >> 16)
    sum_ = ~sum_ & 0xffff
    return sum_


class Answer(enum.Enum):
    PORT_OPEN = 0
    PORT_CLOSED = 1
    TIMEOUT = 2
    HOST_UNREACHABLE = 4


class Ping:
    def __init__(self, src_host, src_port, dst_host, dst_port, socket, count,
                 interval, timeout):
        self.src_host = src_host
        self.src_port = src_port
        self.dst_host = dst_host
        self.dst_port = dst_port
        self.interval = interval
        self.socket = socket
        self.count = count
        self.stat = Stat()
        self.timeout = timeout

    def start(self):
        counter = itertools.count(1)
        while self.count:
            code, resp_time = self.ping(next(counter))
            self.stat.add(code, resp_time, self.dst_host, self.dst_port)
            self.count -= 1
            time.sleep(self.interval)

        self.stat.get()
        print_stat(self.stat)

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
                try:
                    data = self.socket.recv_icmp(16384)
                    type_, code = struct.unpack('!BB', data[35:37])
                    if type_ == 3 and code == 3:
                        return Answer.HOST_UNREACHABLE, 0
                except socket.timeout:
                    pass
                return Answer.TIMEOUT, 0
            resp_time = time.time() - start_time
            answ = struct.unpack('!BBBBIIBB', data[20:34])
            if answ[5] == seq + 1:
                if answ[7] == 18:
                    # rst pack
                    self.socket.sendto(self.build(seq, 4),
                                       (self.dst_host, self.dst_port))
                    return Answer.PORT_OPEN, resp_time
                return Answer.PORT_CLOSED, resp_time
            new_timeout = self.timeout - resp_time
            if new_timeout < 0:
                return Answer.TIMEOUT, 0
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
