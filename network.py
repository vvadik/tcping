import socket


class Network:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_TCP)
# TODO: доделать прослойку и тесты