#!/usr/bin/env python3
import sys, socket, json, select, threading
from utils import *

PORT = 16390
state_change = None


# queue of events
# event class
# each event is concurrent or normal
# run user function to handle state change
# 

class CardGame:
    ## TODO: client provided functions should be initialized to none so that
    ## we can check if they have been provided or not, and either execute
    ## them, skip (if possible), or crash (if we can't skip them)
    def __init__(self):
        self.parent_socket = socket.socket()
        self.child_connections = []
        self.stdin_thread          = None
        
        ## User provided closures
        self.do_turn_func          = None
        self.win_check_func        = None
        self.round_end_func        = None
        self.draw_player_func      = None
        self.round_start_func      = None
        self.mutate_state_func     = None
        self.specialist_turn_func  = None
        self.client_interrupt_func = None
        self.server_interrupt_func = None

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

    def set_client_interrupt_handler(client_interrupt_func):
        self.client_interrupt_func = client_interrupt_func

    def run(self):
        if len(sys.argv) == 2 and sys.argv[2] == '-h':
            #self.is_host = True
            self.setup_lobby()
            self.start_server()       
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

    def setup_parent_connection(self):
        host_addr = sys.argv[3]
        self.name = sys.argv[1]
        
        self.parent_socket.connect((host_addr, PORT))
        send_json({'name': self.name}, self.parent_socket)
        
        while 1:
            data = recv_json(self.parent_socket)
            print(data['msg'])
            if 'DC' in data:
                self.parent_socket.close()
                break
            elif 'START' in data:
                self.start_client()

    def start_client(self):
        if self.do_turn_func == None:
            print("do_turn function not provided, cannot run game!", 
                  file=sys.stderr)
        while 1:
            self.run_client()

    def run_client(self):
        global state_change
        ## Wait for signal that it is my turn
        interrupt, state = wait_until_turn(self.name, self.parent_socket)
        
        ## An interrupt results in a none state until a new state is received
        if interrupt == None:
            self.client_interrupt_func(state)
            return
        

        ## I am the current player so I will look myself up
        player = list(filter(lambda p: p.name == self.name, state['players']))

        ## Draw screen for client
        self.draw_player_func(player, state)
        
        ## Spin off a thread to run the turn.  In the meanwhile we should be
        ## checking for an interrupt signal and the thread finishing
        self.stdin_thread = threading.Thread(target=do_turn_caller, \
                                             args=(player, state,   \
                                                   self.do_turn_func))
        self.stdin_thread.start()
        
        while 1:
            ## Check if we have been interrupted by the server
            i_state = check_for_interrupt(self.parent_socket)
            if not i_state == None:
                if self.client_interrupt_func != None:
                    self.client_interrupt_func(i_state)
                return

            ## If not interrupted check if we have finished our turn yet
            self.stdin_thread.join(0.01)
            if not self.stdin_thread.is_alive():
                ## Send back result to server
                send_json({'STATE_CHANGE':state_change, 'FROM': self.name}, \
                          self.parent_socket)
                break

    def start_server(self):
        ## Make game state

        ## Figure out who's turn it is

        ## Start loop to execute each round

    def play(self):
        ## Round loop
        while 1:

def do_turn_caller(player, state, do_turn_func):
    global state_change

    state_change = do_turn_func(player, state)

def check_for_interrupt(sock):
    sock.settimeout(0.01)
    try:
        data = recv_json(sock)
        if 'INTERRUPT' in data:
            return data['GAMESTATE']
        else return None
    ## No interrupt was received!
    except socket.timeout:
        return None

def wait_until_turn(name, sock):
    while 1:
        sock.settimeout(None)
        data = recv_json(sock)
        if 'SHUTDOWN' in data:
            print("Game shut down!  Exiting.")
            sys.exit(0)
        elif 'TURN' in data and data['TURN'] == name:
            return 1, data['GAMESTATE']
        elif 'INTERRUPT' in data:
            return None, data['GAMESTATE']

#class Player:

#class PlayingCard:

c = CardGame()

c.run()
