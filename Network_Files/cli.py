#!/usr/bin/env python3
import socket, json
from utils import *

sock = socket.socket()

sock.connect(('vm-hw04', 42069))

msg = input("Type a message to send: ")

j = {}

if msg == 'q':
    j['q'] = 1
else:
    j['msg'] = msg

send_json(j, sock)
response = recv_json(sock)

print(response['msg'])

sock.close()
