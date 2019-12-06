#!/usr/bin/env python3
import sys, socket, json, select, threading
from utils import *
from GameClasses import *

PORT = 16390
state_change = None
state_lock = threading.Lock()

standard_deck = [(1, 'H'), (2, 'H'), (3, 'H'), (4, 'H'), (5, 'H'), (6, 'H'), 
                 (7, 'H'), (8, 'H'), (9, 'H'), (10, 'H'), (11, 'H'), (12, 'H'), 
                 (13, 'H'), (1, 'S'), (2, 'S'), (3, 'S'), (4, 'S'), (5, 'S'), 
                 (6, 'S'), (7, 'S'), (8, 'S'), (9, 'S'), (10, 'S'), (11, 'S'), 
                 (12, 'S'), (13, 'S'), (1, 'D'), (2, 'D'), (3, 'D'), (4, 'D'), 
                 (5, 'D'), (6, 'D'), (7, 'D'), (8, 'D'), (9, 'D'), (10, 'D'), 
                 (11, 'D'), (12, 'D'), (13, 'D'), (1, 'C'), (2, 'C'), (3, 'C'), 
                 (4, 'C'), (5, 'C'), (6, 'C'), (7, 'C'), (8, 'C'), (9, 'C'), 
                 (10, 'C'), (11, 'C'), (12, 'C'), (13, 'C')]

class CardGame:
    ## TODO: client provided functions should be initialized to none so that
    ## we can check if they have been provided or not, and either execute
    ## them, skip (if possible), or crash (if we can't skip them)
    def __init__(self):
        self.parent_socket = socket.socket()
        self.child_connections = []
        self.events = []
        self.messages = []
        self.message_lock = Threading.Lock()

        self.init_state_func  = None
        self.state            = None
    
    
    def set_config(self, num_players=(2, 2)):
        self.min_players      = num_players[0]
        self.max_players      = num_players[1]

    def set_init_state(self, init_state_func):
        self.init_state_func = init_state_func

    def run(self):
        ## TODO check to make sure we have the stuff needed to run game
        if len(sys.argv) == 2 and sys.argv[1] == '-h':
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
        
        self.num_players = 0
        self.player_names = []
        
        print("Listening on port %d" % PORT)
        print("Waiting for %d or more players.  Enter 'Q' to quit." \
              % self.min_players)
        
        while True:
            try:
                conn, addr = sock.accept()
                
                data = recv_json(conn)
                name = data['name']

                self.player_names.append(name)
                self.child_connections.append((name, conn, addr))
                self.num_players += 1
                
                print("received a connection from:", name)
                if self.num_players >= self.min_players:
                    print("If all players are present, enter 'Y'")
                for (n, conn, addr) in self.child_connections:
                    send_json({'msg': "Connected %s to the lobby\nThere are now"
                               " %d players connected:\n%s" \
                               % (name, self.num_players, ', '.join(self.player_names))},conn)

            except socket.timeout:
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    ch = sys.stdin.read(1)
                    if self.num_players >= self.min_players and ch == 'Y':
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

    ## Run lobby on client side
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

# client side
def do_turn_caller(game_state, do_turn, server_sock, player, index):
    global state_change
    state_change, message = do_turn(game_state, player, index)
    curr_state = state_change.get_json()
    send_json({'STATE_CHANGE': json.dumps(curr_state)}, \
                          server_sock)
    if message != '':
        send_json({'msg':message}, server_sock)

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
