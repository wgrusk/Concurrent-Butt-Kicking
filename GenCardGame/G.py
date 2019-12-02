#!/usr/bin/env python3
import sys, socket, json
from utils import *

PORT = 16390

class CardGame:
    def __init__(self):
        self.parent_socket = socket.socket()
        self.child_connections = []

    def run(self):
        if len(sys.argv) == 3 and sys.argv[2] == '-h':
            self.is_host = True
            self.setup_lobby()
        elif len(sys.argv) == 4 and sys.argv[2] == '-c':
            self.is_host = False
            self.setup_parent_connection()
        else:
            print("Usage:\n\t[EXE] [USR_NAME] -h to host a game\n\t"
                  "[EXE] [USR_NAME] -c [IP_ADDR] to connect to a game lobby")
            sys.exit(1)

    def setup_lobby(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", PORT))
        players = 1
        sock.listen(1)
        
        while players < 4:
            conn, addr = sock.accept()
            data = recv_json(conn)
            name = data['name']
            print("received a connection from:", name)
            self.child_connections.append((name, conn, addr))
            players += 1
            for (n, conn, addr) in self.child_connections:
                send_json({'msg': "connected %s to the lobby" % name}, conn)

        print("collected 4 players!")

        for (name, conn, addr) in self.child_connections:
            print("disconnecting", name)
            send_json({'msg':'disconnecting!', 'DC': 1}, conn)
            conn.close()

    def setup_parent_connection(self):
        host_addr = sys.argv[3]
        name = sys.argv[1]
        msg = {'name': name}
        self.parent_socket.connect((host_addr, PORT))
        send_json(msg, self.parent_socket)
        
        while 1:
            data = recv_json(self.parent_socket)
            if 'DC' in data:
                self.parent_socket.close()
                break
            else:
                print(data['msg'])

#class Player:

#class PlayingCard:

c = CardGame()

c.run()
