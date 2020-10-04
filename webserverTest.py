import socket
import time

s = socket.socket()

s.bind(('127.0.0.1', 8000))
s.listen(1)
while True:

    client_sock, client_addr = s.accept()
    data = s.recv(1024)

# s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
# # s = socket.socket()
# s.bind(('127.0.0.1', 8000))
# data = s.recv(1024)
# print(data)
#s.listen()
#client_sock, client_addr = s.accept()