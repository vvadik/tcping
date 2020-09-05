#!/usr/bin/python3

import argparse
import socket
import re
import netifaces as ni
from packet import Packet
from ping import Ping


def get_ip():
    for i in ni.interfaces():
        ip = ni.ifaddresses(i)[2][0]['addr']
        if ip != '127.0.0.1':
            return ip


def set_args(args):
    if args.port:
        port = args.port
    else:
        port = 80

    if args.count:
        count = args.count
    else:
        count = 4

    if args.waiting:
        waiting = args.waiting
    else:
        waiting = 2
    return port, count, waiting


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Starting tcping')
    parser.add_argument('website', type=str, metavar='', help='website to ping')

    parser.add_argument('-n', '--number', dest='count', type=int, metavar='',
                        required=False, help='number of requests, default is 4')
    parser.add_argument('-p', '--port', dest='port', type=int, metavar='',
                        required=False, help='port to ping, default is 80')
    parser.add_argument('-w', '--waiting', dest='waiting', type=int, metavar='',
                        required=False, help='Waiting _ seconds for a response,'
                                             'default is 2')

    args = parser.parse_args()

    reg_ip = re.search(r"[A-Z]|[a-z]", args.website)
    dst = args.website
    if reg_ip:
        dst = socket.gethostbyname(f'{args.website}')

    port, count, waiting = set_args(args)

    pack = Packet(get_ip(), 10001, dst, port)
    socket.setdefaulttimeout(waiting)
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    ping = Ping(pack, s, count)
    ping.start()
