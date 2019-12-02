#!/usr/bin/env python3
import socket
import json
from utils import *

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", 42069))

looping = True

while looping:
    sock.listen(1)

    conn, addr = sock.accept()

    data = recv_json(conn)

    if 'q' in data:
        looping = False
        send_json({'msg': 'quitting!'}, conn)
    else:
        print(data['msg'])
        send_json({'msg': 'received message'}, conn)

    conn.close()

sock.close()
