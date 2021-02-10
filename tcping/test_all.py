#!/usr/bin/python3

import unittest
import time
from ping import Ping, Answer


class Network:
    '''
    case 1: Проверка на открытый порт
    Приходит пакетов: 1

    case 2: Проверка на закрытый порт
    Приходит пакетов: 1

    case 3: Проверка на Host Unreachable
    Приходит пакетов: 1

    case 4: Проверка на неизвестные пакеты icmp
    Приходит пакетов: 3

    case 5: Проверка на неизвестные пакеты tcp
    Приходит пакетов: 3

    case 6: Проверка на timeout
    Ничего не приходит

    case 7: Пакеты приходят не в порядке отправки
    Приходит пакетов: 2 в обратном порядке
    '''
    def __init__(self):
        self.case = {1: [b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00"
                         b"\x00\x00\x01\x00\x00\x00\x02P\x12\x04\x00\x00\x00"
                         b"\x00\x00"],
                     2: [b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00"
                         b"\x00\x00\x01\x00\x00\x00\x02P\x14\x04\x00\x00\x00"
                         b"\x00\x00"],
                     3: [b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                         b"\x00\x00\x00\x00\x00\x00\x00\x00\x03\x01\x00\x00"
                         b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                         b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'"
                         b"\x11'\x12\x00\x00\x00\x01"],
                     4: [b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                         b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00"
                         b"\x00\x00\x01\x00\x00\x00\x02P\x12\x04\x00\x00\x00"
                         b"\x00\x00"],
                     5: [b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00',
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00',
                         b"\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                         b"\x00\x00\x00\x04\x00\x00\x00\x05'\x12'\x11\x00"
                         b"\x00\x00\x01\x00\x00\x00\x02P\x12\x04\x00\x00\x00"
                         b"\x00\x00"],
                     7: [b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00',
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00']}
        self.current_case = 0

    def settimeout(self, timeout):
        pass

    def sendto(self, pack, client):
        pass

    def recv(self, count):
        if self.case[self.current_case]:
            pack = self.case[self.current_case][0]
            del self.case[self.current_case][0]
            return pack
        return

    def poll(self, timeout):
        if self.current_case == 6:
            return
        return self


class TestTcping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.socket = Network()
        ip = '127.0.0.1'
        cls.ping = Ping((ip, 10001), (ip, 10002), cls.socket, 2)

    def test_opened_port(self):
        self.socket.current_case = 1

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.PORT_OPEN)

    def test_closed_port(self):
        self.socket.current_case = 2

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.PORT_CLOSED)

    def test_host_unreachable(self):
        self.socket.current_case = 3

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.HOST_UNREACHABLE)

    def test_foreign_pack_icmp(self):
        self.socket.current_case = 4

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.PORT_OPEN)

    def test_foreign_pack_tcp(self):
        self.socket.current_case = 5

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.PORT_OPEN)

    def test_timeout(self):
        self.socket.current_case = 6

        code, time = self.ping.ping(seq=1)
        self.assertEqual(code, Answer.TIMEOUT)

    def test_mix(self):
        self.socket.current_case = 7

        current = time.time()
        self.ping.packages_set[1] = (current, 0)
        self.ping.packages_set[2] = (current, 0)
        self.ping.packages_list.append((1, current, 0))
        self.ping.packages_list.append((2, current, 0))

        seq, result, time_, recv_pack = self.ping.parse_packages_async(1)
        self.assertEqual(seq, 2)
        self.assertEqual(result, Answer.PORT_CLOSED)

        seq, result, time_, recv_pack = self.ping.parse_packages_async(1)
        self.assertEqual(seq, 1)
        self.assertEqual(result, Answer.PORT_CLOSED)
