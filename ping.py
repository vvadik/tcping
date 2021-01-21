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
        self.packages_set = {}  # seq: (time_sent, pack) проверка приходящих
        self.packages_list = []  # [(seq, time_sent, pack), ...] Для сортировки
        # по времени и проверки по таймауту

    def start(self, count, interval):
        counter = itertools.count(1)
        if interval >= self.timeout:
            while count:
                seq = next(counter)
                code, resp_time = self.ping(seq)
                self.stat.add(code, resp_time)
                res = (f'{seq} Ping {self.dst_host}:{self.dst_port} '
                       f'- {code} - time={round(resp_time * 1000, 3)}ms')
                print(res)
                count -= 1
                time.sleep(interval - resp_time)

        else:
            while count:
                seq = next(counter)
                seq, code, resp_time, working = self.ping(seq, write_pack=True,
                                                          interval=interval)

                working = round((time.time() - working), 3)

                count -= 1
                if seq:
                    self.stat.add(code, resp_time)
                    res = (f'{seq} Ping {self.dst_host}:{self.dst_port} '
                           f'- {code} - time={round(resp_time * 1000, 3)}ms')
                    print(res)
                    if interval - working > 0:
                        time.sleep(interval - working)

            while True:
                if not self.packages_list:
                    break
                timeout = round(time.time() - self.packages_list[0][1], 3)

                seq, result, time_, recv_pack \
                    = self.parse_packages_async(timeout)

                if seq and self.packages_list and time_ != -1:
                    i = 0
                    for i in range(len(self.packages_list)):
                        if self.packages_list[i][0] == seq:
                            break
                    del self.packages_list[i]
                    del self.packages_set[seq]

                    self.stat.add(result, time_)
                    res = (f'{seq} Ping {self.dst_host}:{self.dst_port} '
                           f'- {result} - time={round(time_ * 1000, 3)}ms')
                    print(res)

                if time_ == -1:  # timeout from list
                    self.stat.add(result, time_)
                    res = (f'{seq - 1} Ping {self.dst_host}:{self.dst_port} '
                           f'- {result} - time=0ms')
                    print(res)

                if self.debug and seq:
                    sniff(self.packages_set[seq][1], recv_pack)

        self.stat.get()
        print(self.stat.sumup())

    def ping(self, seq, write_pack=False, interval=0):
        if write_pack:
            working_time = time.time()
            self.socket.settimeout(interval)
            tcppacket = self.build(seq, 2)
            start_time = time.time()
            self.packages_set[seq] = (start_time, tcppacket)
            self.packages_list.append((seq, start_time))
            self.socket.sendto(tcppacket, (self.dst_host, self.dst_port))
            while True:

                seq, result, time_, recv_pack \
                    = self.parse_packages_async(interval)
                if seq and self.packages_list and time_ != -1:
                    i = 0
                    for i in range(len(self.packages_list)):
                        if self.packages_list[i][0] == seq:
                            break
                    del self.packages_list[i]
                    del self.packages_set[seq]
                if time_ == -1:  # timeout from list
                    self.stat.add(result, time_)
                    res = (f'{seq - 1} Ping {self.dst_host}:{self.dst_port} '
                           f'- {result} - time=0ms')
                    print(res)
                else:
                    break
            if self.debug and seq:
                sniff(self.packages_set[seq][1], recv_pack)
            return seq, result, time_, working_time

        else:
            self.socket.settimeout(self.timeout)
            tcppacket = self.build(seq, 2)
            start_time = time.time()
            self.socket.sendto(tcppacket, (self.dst_host, self.dst_port))
            result, time_, recv_pack = self.parse_packages(start_time, seq)
            if self.debug:
                sniff(tcppacket, recv_pack)
            return result, time_

    def parse_packages_async(self, socket_timeout):
        new_timeout = socket_timeout
        if (self.packages_list and
                round(time.time() - self.packages_list[0][1],
                      3) > self.timeout):
            seq = self.packages_list[0][0]
            del self.packages_list[0]
            del self.packages_set[seq]
            return seq, Answer.TIMEOUT, -1, None

        while True:
            sock = self.socket.poll(new_timeout * 1000)
            if not sock:
                return None, None, 0, None
            else:
                resp_time = time.time()
                data = sock.recv(16384)
                # icmp check
                type_, code = struct.unpack('!BB', data[20:22])
                if type_ == 3 and code == 1:
                    src_port, dst_port, dst_seq = struct.unpack('!HHL',
                                                                data[48:56])
                    if (self.src_port == src_port and self.dst_port == dst_port
                            and dst_seq in self.packages_set):
                        past_time = round(resp_time -
                                          self.packages_set[dst_seq][0], 3)
                        if past_time > self.timeout:
                            return dst_seq, Answer.TIMEOUT, 0, data
                        return (dst_seq, Answer.HOST_UNREACHABLE,
                                resp_time - self.packages_set[dst_seq][0],
                                data)
                # tcp check
                answ = struct.unpack('!BBBBIIBB', data[20:34])
                if answ[5] - 1 in self.packages_set:
                    past_time = round(resp_time -
                                      self.packages_set[answ[5] - 1][0], 3)
                    if past_time > self.timeout:
                        return answ[5] - 1, Answer.TIMEOUT, 0, data
                    if answ[7] == 18:
                        # rst pack
                        self.socket.sendto(self.build(answ[5] - 1, 4),
                                           (self.dst_host, self.dst_port))
                        return (answ[5] - 1, Answer.PORT_OPEN,
                                resp_time - self.packages_set[answ[5] - 1][0],
                                data)
                    return (answ[5] - 1, Answer.PORT_CLOSED,
                            resp_time - self.packages_set[answ[5] - 1][0],
                            data)
                new_timeout = new_timeout - resp_time
                if new_timeout < 0:
                    return None, None, 0, None
                continue

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
            seq,  # SEQ
            0,  # ACK
            5 << 4,  # Data Offset
            flags,  # Flags
            1024,  # Window
            0,  # Checksum
            0  # Urgent pointer
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
