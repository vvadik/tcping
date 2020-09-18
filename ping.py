#!/usr/bin/python3

import struct
import array
import socket
import time
from statistics import Stat


class Ping:
    def __init__(self, pack, s, count, inf=False):
        self.pack = pack
        self.s = s
        self.count = count
        self.stat = Stat()
        self.inf = inf
        self.timeout = s.gettimeout()

    def start(self):
        i = 0
        while True:
            if not self.inf and i >= self.count:
                break
            response, reasone, resp_time = self.ping(i + 1)
            self.result(response, reasone, resp_time)
            i += 1
            time.sleep(1)
        self.stat.get()

    def ping(self, seq):
        self.s.settimeout(self.timeout)
        tcppacket = self.build(seq)
        start_time = time.time()

        self.s.sendto(tcppacket, (self.pack.dst_host, 0))

        while True:
            try:
                data = self.s.recv(1024)
            except socket.timeout:
                return False, 'timeout', 0
            resp_time = time.time() - start_time
            print('TIME_MS', resp_time)
            answ = struct.unpack('!IBB', data[28:34])
            if answ[0] == seq + 1:
                if answ[2] == 18:
                    return True, 'port is open', resp_time
                return False, 'connect refused', resp_time
            new_timeout = self.timeout - resp_time
            if new_timeout < 0:
                return False, 'timeout', 0
            self.s.settimeout(new_timeout)
            print('NEW TIMEOUT', new_timeout)
            continue

    def result(self, response, reasone, resp_time):
        if resp_time != 0:
            resp_time = round(resp_time, 3)
            self.stat.time.append(resp_time)
        self.stat.results[response] += 1

        res = f'Ping {self.pack.dst_host}:{self.pack.dst_port} ' \
              f'- {reasone} - time={resp_time}ms'
        print(res)

    def build(self, seq):
        packet = struct.pack(
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
            len(packet)
        )

        checksum = self.chksum(pseudo_hdr + packet)
        packet = packet[:16] + struct.pack('H', checksum) + packet[18:]

        return packet

    def chksum(self, packet):
        """
        This function I took from scapy's open source code
        """
        if len(packet) % 2 != 0:
            packet += b'\0'

        res = sum(array.array("H", packet))
        res = (res >> 16) + (res & 0xffff)
        res += res >> 16

        return (~res) & 0xffff
