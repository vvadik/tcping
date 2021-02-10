#!/usr/bin/python3

import argparse
import sys
import os
import socket
from ping import Ping
import platform
from network import Network


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


def parse_args():
    parser = argparse.ArgumentParser(description='Starting tcping')
    parser.add_argument('host', type=str, help='host to ping')

    parser.add_argument('-n', '--number', dest='count',
                        type=int, required=False,
                        help='number of requests, default is infinity',
                        default=float('Inf'))
    parser.add_argument('-p', '--port', dest='port', type=int,
                        required=False, help='port to ping, default is 80',
                        default=80)
    parser.add_argument('-w', '--waiting', dest='waiting',
                        type=int, required=False,
                        help='Response wait timeout, in seconds, '
                             'default is 5',
                        default=5)
    parser.add_argument('--from-ip', dest='ip',
                        type=str, required=False,
                        help='Set preferred ip')
    parser.add_argument('-i', '--interval', type=float, required=False,
                        help='Interval between pings in seconds', default=1)
    parser.add_argument('-d', '--debug', dest='debug', default=False,
                        action='store_true', required=False)
    args = parser.parse_args()
    return args


def _check_port(s):
    for port in range(49152, 65535):
        try:
            s.tcp.bind(('', port))
        except socket.error:
            pass
        else:
            return port


if __name__ == '__main__':
    if platform.system() == 'Windows':
        sys.stderr.write('It only works on Linux OS\n')
        sys.exit(1)

    args = parse_args()
    dst = socket.gethostbyname(args.host)
    ip = args.ip
    if dst == '127.0.0.1':
        ip = '127.0.0.1'
    if not ip:
        ip = get_ip()

    if os.geteuid() != 0:
        sys.stderr.write('Use it with sudo\n')
        sys.exit(1)

    s = Network()
    port = _check_port(s)

    ping = Ping((ip, port), (dst, args.port), s, args.waiting, args.debug)
    try:
        ping.start(args.count, args.interval)
    except KeyboardInterrupt:
        sys.exit()
