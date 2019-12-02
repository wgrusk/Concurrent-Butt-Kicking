#!/usr/bin/env python3
import sys, socket, json, select
from utils import *

PORT = 16390

class CardGame:
    def __init__(self):
        self.parent_socket = socket.socket()
        self.child_connections = []
        
    def set_config(self, hand_size_init=5, hand_size_max=None, 
                   deck=playing_cards, secondary_deck=None, num_players=(2, 2), 
                   turn_order="inorder", interrupts=False, first_player=0, 
                   specialist_order="end"):
        self.hand_size_init   = hand_size_init
        self.secondary_deck   = secondary_deck
        self.turn_order       = turn_order
        self.interrupts       = interrupts
        self.first_player     = first_player
        self.hand_size_max    = hand_size_max
        self.deck             = deck
        self.min_players      = num_players[0]
        self.max_players      = num_players[1]
        self.specialist_order = specialist_order

    def set_win_condition(win_check_func):
        self.win_check_func = win_check_func

    def set_do_turn(do_turn_func):
        self.do_turn_func = do_turn_func

    def set_draw_player(draw_player_func):
        self.draw_player_func = draw_player_func

    def set_mutate_state(mutate_state_func):
        self.mutate_state_func = mutate_state_func

    def set_round_start(round_start_func):
        self.round_start_func = round_start_func

    def set_round_end(round_end_func):
        self.round_end_func = round_end_func

    def set_specialist_turn(specialist_turn_func):
        self.specialist_turn_func = specialist_turn_func

    def run(self):
        if len(sys.argv) == 2 and sys.argv[2] == '-h':
            #self.is_host = True
            self.setup_lobby()
        elif len(sys.argv) == 4 and sys.argv[2] == '-c':
            #self.is_host = False
            self.setup_parent_connection()
        else:
            print("Usage:\n\t[EXE] -h to host a game\n\t"
                  "[EXE] [USR_NAME] -c [IP_ADDR] to connect to a game lobby")
            sys.exit(1)

    def setup_lobby(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.10)
        sock.bind(("", PORT))
        sock.listen(1)
        
        players = 0
        player_names = []
        
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
                                            

        print("Let the games begin!")
        for (name, conn, addr) in self.child_connections:
            send_json({'msg':'Starting the game!', 'START': 1}, conn)

        self.start_server()       

    def setup_parent_connection(self):
        host_addr = sys.argv[3]
        self.name = sys.argv[1]
        msg = {'name': self.name}
        self.parent_socket.connect((host_addr, PORT))
        send_json(msg, self.parent_socket)
        
        while 1:
            data = recv_json(self.parent_socket)
            print(data['msg'])
            if 'DC' in data:
                self.parent_socket.close()
                break
            elif 'START' in data:
                self.start_client()

    def start_client(self):
        ## Wait for signal that it is my turn
        state = wait_until_turn(self.name, self.parent_socket)
        
        ## I am the current player so I will look myself up
        player = list(filter(lambda p: p.name == self.name, state['players']))

        ## Draw screen for client
        self.draw_player_func(player, state)
        
        ## Do my turn
        state_change = self.do_turn(player, state)

        ## Send back result to server
        send_json({'STATE_CHANGE':state_change, 'FROM': self.name}, \
                  self.parent_socket)

    def start_server(self):
        ## Make game state

        ## Figure out who's turn it is

        ## Start loop to execute each round

    def play(self):
        ## Round loop
        while 1:




def wait_until_turn(name, sock):
    while 1:
        sock.settimeout(None)
        data = recv_json(sock)
        if 'SHUTDOWN' in data:
            print("Game shut down!  Exiting.")
            sys.exit(0)
        elif 'TURN' in data and data['TURN'] == name:
            return data['GAMESTATE']

#class Player:

#class PlayingCard:

c = CardGame()

c.run()
