#!/usr/bin/python3

import argparse
import sys
import socket
import re
from package import Package
from ping import Ping


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Starting tcping')
    parser.add_argument('website', type=str, metavar='',
                        help='website to ping')

    parser.add_argument('-n', '--number', dest='count',
                        type=int, metavar='', required=False,
                        help='number of requests, default is 4',
                        default=4)
    parser.add_argument('-p', '--port', dest='port', type=int, metavar='',
                        required=False, help='port to ping, default is 80',
                        default=80)
    parser.add_argument('-w', '--waiting', dest='waiting',
                        type=int, metavar='', required=False,
                        help='Waiting _ seconds for a response, default is 2',
                        default=2)
    parser.add_argument('-ip', dest='ip',
                        type=str, metavar='', required=False,
                        help='Type -ip to set preferred ip', default=get_ip())
    parser.add_argument('-i', '--infinity', dest='inf',
                        type=bool, metavar='', required=False,
                        help='Set True for infinity pinging',
                        default=False)

    args = parser.parse_args()

    dst = args.website
    if re.search(r"[A-Z]|[a-z]", args.website):
        dst = socket.gethostbyname(f'{args.website}')
    if args.website in ['localhost', '127.0.0.1']:
        args.ip = '127.0.0.1'

    pack = Package(args.ip, 10000, dst, args.port)
    socket.setdefaulttimeout(args.waiting)
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    ping = Ping(pack, s, args.count, args.inf)
    try:
        ping.start()
    except KeyboardInterrupt:
        sys.exit()
