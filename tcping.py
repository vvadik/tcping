#!/usr/bin/python3

import argparse
import sys
import socket
import re
from ping import Ping
import platform


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


def parse_args():
    parser = argparse.ArgumentParser(description='Starting tcping')
    parser.add_argument('host', type=str,
                        help='host to ping')

    parser.add_argument('-n', '--number', dest='count',
                        type=int, required=False,
                        help='number of requests, default is 4',
                        default=float('Inf'))
    parser.add_argument('-p', '--port', dest='port', type=int,
                        required=False, help='port to ping, default is 80',
                        default=80)
    parser.add_argument('-w', '--waiting', dest='waiting',
                        type=int, required=False,
                        help='Response wait timeout, in seconds, default is 2',
                        default=2)
    parser.add_argument('--from-ip', dest='ip',
                        type=str, required=False,
                        help='Type -ip to set preferred ip')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if platform.system() == 'Windows':
        print('It only works on Linux OS')
        sys.exit()
    args = parse_args()
    dst = socket.gethostbyname(f'{args.host}')
    ip = args.ip
    if args.host == '127.0.0.1':
        ip = '127.0.0.1'
    if not ip:
        ip = get_ip()

    socket.setdefaulttimeout(args.waiting)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except PermissionError:
        print('Use it with sudo')
        sys.exit()

    ping = Ping(ip, 10001, dst, args.port, s, args.count)
    try:
        ping.start()
    except KeyboardInterrupt:
        sys.exit()
