import socket


class Network:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_TCP)
        self.socket_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                         socket.IPPROTO_ICMP)
        self.socket_icmp.settimeout(0.1)

    def settimeout(self, timeout):
        self.socket.settimeout(timeout)

    def sendto(self, pack, client):
        self.socket.sendto(pack, client)

    def recv(self, count):
        return self.socket.recv(count)

    def recv_icmp(self, count):
        return self.socket_icmp.recv(count)
