#!/usr/bin/python3

import argparse
import socket
import re
from packet import Packet
from ping import Ping


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((socket.gethostbyname('google.com'), 80))
    return s.getsockname()[0]


def set_args(args):
    port = args.port
    if not port:
        port = 80

    count = args.count
    if not count:
        count = 4

    waiting = args.waiting
    if not waiting:
        waiting = 2

    ip = args.ip
    if not ip:
        ip = get_ip()

    inf = args.inf
    if not inf:
        inf = False

    reg_ip = re.search(r"[A-Z]|[a-z]", args.website)
    dst = args.website
    if reg_ip:
        dst = socket.gethostbyname(f'{args.website}')
    return port, count, waiting, ip, inf, dst


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Starting tcping')
    parser.add_argument('website', type=str, metavar='',
                        help='website to ping')

    parser.add_argument('-n', '--number', dest='count',
                        type=int, metavar='', required=False,
                        help='number of requests, default is 4')
    parser.add_argument('-p', '--port', dest='port', type=int, metavar='',
                        required=False, help='port to ping, default is 80')
    parser.add_argument('-w', '--waiting', dest='waiting',
                        type=int, metavar='', required=False,
                        help='Waiting _ seconds for a response, default is 2')
    parser.add_argument('-ip', dest='ip',
                        type=str, metavar='', required=False,
                        help='Type -ip to set preferred ip')
    parser.add_argument('-i', '--infinity', dest='inf',
                        type=bool, metavar='', required=False,
                        help='Set True for infinity pinging')

    args = parser.parse_args()

    port, count, waiting, ip, inf, dst = set_args(args)
    pack = Packet(ip, 10001, dst, port)
    socket.setdefaulttimeout(waiting)
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    ping = Ping(pack, s, count, inf)
    try:
        ping.start()
    except KeyboardInterrupt:
        exit()
