#!/usr/bin/env python3
import sys, socket, json, select, threading
from utils import *
from Deck import Deck
from Hand import Hand
from Player import Player
from PlayingCard import PlayingCard
from GameState import GameState
from StandardDeck import *

PORT = 16390
state_global = None
state_lock = threading.Lock()
messages = []
messages_lock = threading.Lock()
events = []
events_lock = threading.Lock()

#################### PLAYER PROVIDED #######################


#################### END PLAYER PROVIDED #######################


class CardGame:

    def __init__(self):
        self.parent_socket = socket.socket()
        self.child_connections = []
        self.stdin_thread      = None
        self.player_names      = []
        self.num_players       = 0
        ## User provided closures
        self.init_state_func         = None
        self.do_turn_func            = None
        self.draw_player_func        = None
        self.client_interrupt_func   = None
        self.server_interrupt_func   = None
        self.name                    = None


    def set_config(num_players):
        self.req_num_players = req_num_players

    def set_init_state(self, init_state_func):
        self.init_state_func = init_state_func

    def set_do_turn(self, do_turn_func):
        self.do_turn_func = do_turn_func

    def set_draw_player(self, draw_player_func):
        self.draw_player_func = draw_player_func

    def set_client_interrupt_handler(self, client_interrupt_func):
        self.client_interrupt_func = client_interrupt_func

    def set_server_interrupt_handler(self, server_interrupt_func):
        self.server_interrupt_func = server_interrupt_func

    def run(self):
        if len(sys.argv) == 2 and sys.argv[1] == '-h':
            self.setup_lobby()
            self.start_server()       
        elif len(sys.argv) == 4 and sys.argv[2] == '-c':
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
        
        print("Listening on port %d" % PORT)
        print("Waiting for %d or more players.  Enter 'Q' to quit." \
              % self.num_players)
        
        while True:
            try:
                conn, addr = sock.accept()
                
                data = recv_json(conn)
                name = data['name']

                self.num_players += 1
                self.player_names.append(name)
                self.child_connections.append((name, conn, addr, self.num_players))
                
                print("received a connection from:", name)
                if self.num_players >= self.req_num_players:
                    print("If all players are present, enter 'Y'")
                for (n, conn, addr, num) in self.child_connections:
                    send_json({'msg': "Connected %s to the lobby\nThere are now"
                               " %d players connected:\n%s" \
                               % (name, self.num_players, ', '.join(self.player_names))},conn)

            except socket.timeout:
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    ch = sys.stdin.read(1)
                    if self.num_players >= self.req_num_players and ch == 'Y':
                        print("Starting the game!")
                        break
                    elif ch == 'Q':
                        for (name, conn, addr, num) in self.child_connections:
                            print("disconnecting", name)
                            send_json({'msg':'disconnecting!', 'DC': 1}, conn)
                            conn.close()
                        sys.exit(0)
                    else:
                        ## Flush extra chars from line if they dont match
                        sys.stdin.readline()

        print("Let the games begin!")

        for (name, conn, addr, num) in self.child_connections:
            send_json({'msg':'Starting the game!', 'START': 1}, conn)

    def setup_parent_connection(self):
        host_addr = sys.argv[3]
        self.name = sys.argv[1]
        
        self.parent_socket.connect((host_addr, PORT))
        send_json({'name': self.name}, self.parent_socket)
        
        while True:
            data = recv_json(self.parent_socket)
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
        global state_global

        interupt, state = wait_until_turn(self.name, self.parent_socket)

		game_state = reconstruct_state(state)

		## look up self
		count = 0;
		player = None
		for p in game_state.players:
			if p.name == self.name:
				player = p
				count += 1 

        if interupt == False:
			new_state, message = do_turn_caller(game_state)
			send_json({'INTERRUPT_RUN': new_state.get_json(), 'MSG': message, 'FROM': self.name}, self.parent_socket)
	    elif: interupt == True:
	    	new_state, message = client_interrupt_func(game_state) 
	    	send_json({'INTERRUPT_STATE': new_state.get_json(), 'MSG': message, 'FROM': self.name}, self.parent_socket)



    def start_server(self):
        self.state = self.init_state_func(self)

        ## Figure out who's turn it is (defaults to first player)
        monitor_threads = []
        for connect in self.child_connections:
            monitor_threads.append(threading.Thread(target=update_state, \
                                             args=(connect, self.child_connections, self.server_interrupt_func)))

        monitor_threads.append(threading.Thread(target=handle_inbox, args = (self.child_connections,)))

        for thread in monitor_threads:
            thread.start()

        first_name = self.state.players[0].name

        child_connect = [conn for conn in self.child_connections if conn[0] == first_name]

        [(name, connect, addr, num)] = child_connect

        state_data = self.state.get_json()

        send_json({'TURN':first_name, 'PLAYER_DATA': json.dumps(state_data)}, connect)

        for thread in monitor_threads:
            thread.join()

# player side           
def wait_until_turn(name, sock):
    while True:
        sock.settimeout(None)
        data = recv_json(sock)
        if 'SHUTDOWN' in data:
            print("Game shut down!  Exiting.")
            sys.exit(0)
        elif 'TURN' in data and data['TURN'] == name:
            return True, data['PLAYER_DATA']
        elif 'INTERRUPT_RUN' in data:
        	messages_lock.acquire()
        	messages.append(message)
        	messages_lock.release()
        	return False, data['PLAYER_DATA']


        # print("END")




############################### FUNCTIONS TO HANDLE STATE JSON ###########################
def reconstruct_state(state):
    game_state = json.loads(state)
    players = []
    for player in game_state['players']:
        cards = player['hand']
        points = player['points']
        name = player['name']
        hand = reconstruct_hand(cards)
        temp_player = Player(hand, name)
        temp_player.points = points
        players.append(temp_player)
    game = GameState(players)

    table_cards = game_state['table_cards']
    table_deck = reconstruct_deck(table_cards)
    game.cards_on_table = table_deck
    game.curr_player = game_state['curr_player']

    if 'primary_deck' in game_state:
        game.primary_deck = reconstruct_deck(game_state['primary_deck'])
    if 'played_primary' in game_state:
        game.played_primary = reconstruct_deck(game_state['played_primary'])
    if 'secondary_deck' in game_state:
        game.secondary_deck = reconstruct_deck(game_state['secondary_deck'])
    if 'played_secondary' in game_state:
        game.played_secondary = reconstruct_deck(game_state['played_secondary'])
    if 'judge' in game_state:
        game.judge = game_state['judge']
    if 'curr_rank' in game_state:
        game.curr_rank = game_state['curr_rank']
    if 'last_move' in game_state:
        game.last_move = reconstruct_deck(game_state['last_move'])
    return game

def reconstruct_deck(card_list):
    cards = []
    for card in card_list:
        cards.append(PlayingCard(card))
    return Deck(cards)

def reconstruct_hand(card_list):
    cards = []
    for card in card_list:
        cards.append(PlayingCard(card))
    return cards
