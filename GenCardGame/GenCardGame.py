#!/usr/bin/env python3
import sys, socket, json, select
from utils import *

PORT = 16390

class CardGame:
    def __init__(self):
        self.parent_socket = socket.socket()
        self.child_connections = []
        self.min_players = 4

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
        sock.settimeout(0.15)
        sock.bind(("", PORT))
        sock.listen(1)
        
        players = 1
        player_names = [sys.argv[1]]
        
        print("Listening on port %d" % PORT)
        print("Waiting for %d or more players.  Enter 'Q' to quit." \
              % self.min_players)
        
        while 1:
            try:
                conn, addr = sock.accept()
                
                data = recv_json(conn)
                name = data['name']
                player_names.append(name)
                self.child_connections.append((name, conn, addr))
                players += 1
                
                print("received a connection from:", name)
                if players >= self.min_players:
                    print("If all players are present, enter 'Y'")
                for (n, conn, addr) in self.child_connections:
                    send_json({'msg': "Connected %s to the lobby\nThere are now"
                               " %d players connected:\n%s" \
                               % (name, players, ', '.join(player_names))},conn)
            except socket.timeout:
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    ch = sys.stdin.read(1)
                    if players >= self.min_players and ch == 'Y':
                        print("Starting the game!")
                        break
                    elif ch == 'Q':
                        for (name, conn, addr) in self.child_connections:
                            print("disconnecting", name)
                            send_json({'msg':'disconnecting!', 'DC': 1}, conn)
                            conn.close()
                        sys.exit(0)
                    else:
                        ## Flush extra chars from line if they dont match
                        sys.stdin.readline()
                                            

        print("collected %d players!" % players)
        print("Let the games begin!")
        for (name, conn, addr) in self.child_connections:
            send_json({'msg':'Starting the game!', 'DC': 1}, conn)
            conn.close()


    def setup_parent_connection(self):
        host_addr = sys.argv[3]
        name = sys.argv[1]
        msg = {'name': name}
        self.parent_socket.connect((host_addr, PORT))
        send_json(msg, self.parent_socket)
        
        while 1:
            data = recv_json(self.parent_socket)
            print(data['msg'])
            if 'DC' in data:
                self.parent_socket.close()
                break

#class Player:

#class PlayingCard:

c = CardGame()

c.run()
