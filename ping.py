#!/usr/bin/python3

import struct
import itertools
import socket
import time
import enum
from statistics import Stat
from sniffer import sniff


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
    def __init__(self, source, destination, network, timeout, debug=False):
        self.src_host, self.src_port = source
        self.dst_host, self.dst_port = destination
        self.socket = network
        self.stat = Stat()
        self.timeout = timeout
        self.debug = debug

    def start(self, count, interval):
        counter = itertools.count(1)
        while count:
            code, resp_time = self.ping(next(counter))
            self.stat.add(code, resp_time)
            res = (f'Ping {self.dst_host}:{self.dst_port} '
                   f'- {code} - time={round(resp_time * 1000, 3)}ms')
            print(res)
            count -= 1
            if interval - resp_time > 0:
                time.sleep(interval - resp_time)

        self.stat.get()
        print(self.stat.sumup())

    def ping(self, seq):
        self.socket.settimeout(self.timeout)
        tcppacket = self.build(seq, 2)

        start_time = time.time()
        self.socket.sendto(tcppacket, (self.dst_host, self.dst_port))
        result, time_, recv_pack = self.parse_packages(start_time, seq)
        if self.debug:
            sniff(tcppacket, recv_pack)
        return result, time_

    def parse_packages(self, start_time, seq):
        new_timeout = self.timeout
        while True:
            sock = self.socket.poll(new_timeout * 1000)
            if not sock:
                return Answer.TIMEOUT, 0, None
            else:
                resp_time = time.time() - start_time
                data = sock.recv(16384)
                # icmp check
                type_, code = struct.unpack('!BB', data[20:22])
                if type_ == 3 and code == 1:
                    src_port, dst_port, dst_seq = struct.unpack('!HHL',
                                                                data[48:56])
                    if (self.src_port == src_port and self.dst_port == dst_port
                            and seq == dst_seq):
                        return Answer.HOST_UNREACHABLE, 0, data
                # tcp check
                answ = struct.unpack('!BBBBIIBB', data[20:34])
                if answ[5] == seq + 1:
                    if answ[7] == 18:
                        # rst pack
                        self.socket.sendto(self.build(seq, 4),
                                           (self.dst_host, self.dst_port))
                        return Answer.PORT_OPEN, resp_time, data
                    return Answer.PORT_CLOSED, resp_time, data
                new_timeout = self.timeout - resp_time
                if new_timeout < 0:
                    return Answer.TIMEOUT, 0, None
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
