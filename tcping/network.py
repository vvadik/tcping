import socket
import select


class Network:
    def __init__(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                 socket.IPPROTO_TCP)
        self.icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                  socket.IPPROTO_ICMP)
        self.fd_to_socket = {self.tcp.fileno(): self.tcp,
                             self.icmp.fileno(): self.icmp}
        self.sockets = select.poll()
        self.sockets.register(self.tcp, select.POLLIN)
        self.sockets.register(self.icmp, select.POLLIN)

    def settimeout(self, timeout):
        self.tcp.settimeout(timeout)

    def sendto(self, pack, client):
        self.tcp.sendto(pack, client)

    def recv(self, count):
        return self.tcp.recv(count)

    def recv_icmp(self, count):
        return self.icmp.recv(count)

    def poll(self, timeout):
        number = self.sockets.poll(timeout)
        if number:
            return self.fd_to_socket[number[0][0]]
        return number
