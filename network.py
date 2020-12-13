import socket


class Network:
    def __init__(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                 socket.IPPROTO_TCP)
        self.icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                  socket.IPPROTO_ICMP)
        # self.socket_icmp.settimeout(0.1)

    def settimeout(self, timeout):
        self.tcp.settimeout(timeout)

    def sendto(self, pack, client):
        self.tcp.sendto(pack, client)

    def recv(self, count):
        return self.tcp.recv(count)

    def recv_icmp(self, count):
        return self.icmp.recv(count)
