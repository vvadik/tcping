#!/usr/bin/python3

import struct
import array
import socket
import time
from statistics import Stat


def start(s, pack, count):
    stat = Stat()
    for i in range(count):
        tcppacket = build(pack)
        start_time = time.time()

        s.sendto(tcppacket, (pack.dst_host, 0))

        try:
            data = s.recv(1024)
        except socket.timeout:
            result(pack, 'timeout', 0, stat, 'fail')
            continue
        answ = struct.unpack('!IBB', data[28:34])
        if answ[0] == 42345 and answ[2] == 18:
            time_ms = round((time.time() - start_time) * 1000, 3)
            result(pack, 'port is open', time_ms, stat, 'success')
        time.sleep(1)
    stat.get()


def result(pack, msg, answ_time, stat, request):
    if time != 0:
        stat.time.append(answ_time)
    stat.results[request] += 1

    res = f'Ping {pack.dst_host}:{pack.dst_port} - {msg} - time={answ_time}ms'
    print(res)


def build(tcppacket):
    packet = struct.pack(
        '!HHIIBBHHH',
        tcppacket.src_port,  # Source Port
        tcppacket.dst_port,  # Destination Port
        42344,              # SEQ
        0,              # ACK
        5 << 4,         # Data Offset
        2,     # Flags
        1024,           # Window
        0,              # Checksum
        0               # Urgent pointer
    )

    pseudo_hdr = struct.pack(
        '!4s4sHH',
        socket.inet_aton(tcppacket.src_host),    # Source Address
        socket.inet_aton(tcppacket.dst_host),    # Destination Address
        socket.IPPROTO_TCP,                 # PTCL
        len(packet)                         # TCP Length
    )

    checksum = chksum(pseudo_hdr + packet)
    packet = packet[:16] + struct.pack('H', checksum) + packet[18:]

    return packet


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
