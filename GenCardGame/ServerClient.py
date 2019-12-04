#!/usr/bin/env python3
import sys, socket, json, select, threading
from utils import *

from Deck import Deck
from Hand import Hand
from Player import Player
from PlayingCard import PlayingCard
from GameState import GameState

PORT = 16390
state_change = None

standard_deck = [(1, 'H'), (2, 'H'), (3, 'H'), (4, 'H'), (5, 'H'), (6, 'H'), 
                 (7, 'H'), (8, 'H'), (9, 'H'), (10, 'H'), (11, 'H'), (12, 'H'), 
                 (13, 'H'), (1, 'S'), (2, 'S'), (3, 'S'), (4, 'S'), (5, 'S'), 
                 (6, 'S'), (7, 'S'), (8, 'S'), (9, 'S'), (10, 'S'), (11, 'S'), 
                 (12, 'S'), (13, 'S'), (1, 'D'), (2, 'D'), (3, 'D'), (4, 'D'), 
                 (5, 'D'), (6, 'D'), (7, 'D'), (8, 'D'), (9, 'D'), (10, 'D'), 
                 (11, 'D'), (12, 'D'), (13, 'D'), (1, 'C'), (2, 'C'), (3, 'C'), 
                 (4, 'C'), (5, 'C'), (6, 'C'), (7, 'C'), (8, 'C'), (9, 'C'), 
                 (10, 'C'), (11, 'C'), (12, 'C'), (13, 'C')]

STATE = None

MESSAGES_ALL = []

def init_state_bs(game):
    """initial BS state"""
    cards = []

    for card in standard_deck:
        cards.append(PlayingCard(card))

    deck1 = Deck(cards)

    deck1.shuffle()

    players = []

    hands = deck1.divide_deck(game.num_players)

    for i in range(game.num_players):
        players.append(Player(hands[i], game.player_names[i]))

    state = GameState(players)

    return state

def do_turn(game):
    """do turn BS"""
    print("which card(s) do you want to play?")

    num = input("number (1 - 13): ")
    suit = input("suit (D, H, C, or S): ")

    card_to_play = PlayingCard((int(num), suit))

    played = game.players[0].hand.pick_card(card_to_play)

    message = ''
    if played != None:
        message = ("player one played %s of %s" % (card_to_play.rank_string(), card_to_play.suit_string()))

    game.players[0].hand.print_hand()

    return game, message

def print_game(game):
    game.players[0].hand.print_hand_vertical()





# def broadcast(prompt, sock):
#     send_json({'msg':'Starting the game!', 'START': 1}, conn)



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
        self.init_state_func         = None
        self.do_turn_func            = None
        # self.win_check_func        = None
        # self.round_end_func        = None
        self.draw_player_func      = None
        # self.round_start_func      = None
        # self.mutate_state_func     = None
        # self.specialist_turn_func  = None
        # self.client_interrupt_func = None
        # self.server_interrupt_func = None
        self.state                   = None

    def set_config(self,  
                   deck=standard_deck, secondary_deck=None, num_players=(2, 2), 
                   turn_order="inorder", interrupts=False, first_player=0, 
                   specialist_order="end"):
        # self.secondary_deck   = secondary_deck
        # self.turn_order       = turn_order
        # self.interrupts       = interrupts
        self.first_player     = first_player
        self.deck             = deck
        self.min_players      = num_players[0]
        self.max_players      = num_players[1]
        # self.specialist_order = specialist_order

        self.player_names     = []
        self.num_players      = 0

    # def set_win_condition(win_check_func):
    #     self.win_check_func = win_check_func

    def set_init_state(self, init_state_func):
        self.init_state_func = init_state_func

    def set_do_turn(self, do_turn_func):
        self.do_turn_func = do_turn_func

    def set_draw_player(self, draw_player_func):
        self.draw_player_func = draw_player_func

    # def set_mutate_state(mutate_state_func):
    #     self.mutate_state_func = mutate_state_func

    # def set_round_start(round_start_func):
    #     self.round_start_func = round_start_func

    # def set_round_end(round_end_func):
    #     self.round_end_func = round_end_func

    # def set_specialist_turn(specialist_turn_func):
    #     self.specialist_turn_func = specialist_turn_func

    # def set_client_interrupt_handler(client_interrupt_func):
    #     self.client_interrupt_func = client_interrupt_func

    ## starts game by processing arguments WORKS
    def run(self):
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

    # host makes the lobby
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

    def setup_parent_connection(self):
        host_addr = sys.argv[3]
        self.name = sys.argv[1]

        print("%s is port" % host_addr)
        
        self.parent_socket.connect((host_addr, PORT))
        send_json({'name': self.name}, self.parent_socket)
        
        while True:
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

        print("printing sock")
        print(self.parent_socket)

        interrupt, state = wait_until_turn(self.name, self.parent_socket)

        game_state = reconstruct_state(state)
        
        ## An interrupt results in a none state until a new state is received
        if interrupt == None:
            self.client_interrupt_func(game_state)
            return
        

        ## I am the current player so I will look myself up
        player = list(filter(lambda p: p.name == self.name, game_state.players))

        ## Draw screen for client
        self.draw_player_func(game_state)
        
        ## Spin off a thread to run the turn.  In the meanwhile we should be
        ## checking for an interrupt signal and the thread finishing
        self.stdin_thread = threading.Thread(target=do_turn_caller, \
                                             args=(game_state,   \
                                                   self.do_turn_func))
        self.stdin_thread.start()
        
        while True:
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

        self.state = self.init_state_func(self)

        ## Figure out who's turn it is (defaults to first player)

        first_name = self.state.players[0].name

        child_connect = [conn for conn in self.child_connections if conn[0] == first_name]


        [(name, connect, addr)] = child_connect

        state_data = self.state.get_json()

        ## Start loop to execute each round
        count = 1
        while True:
            if count == 1:
                send_json({'TURN':first_name, 'PLAYER_DATA': json.dumps(state_data)}, connect)
                count += 1
            
def wait_until_turn(name, sock):
    while True:
        sock.settimeout(None)
        data = recv_json(sock)
        print(data)
        if 'SHUTDOWN' in data:
            print("Game shut down!  Exiting.")
            sys.exit(0)
        elif 'TURN' in data and data['TURN'] == name:
            return 1, data['PLAYER_DATA']
        elif 'INTERRUPT' in data:
            return None, data['GAMESTATE']
        print("END")

def do_turn_caller(game_state, do_turn):
    STATE = do_turn(game_state)


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

    if 'primary_deck' in game_state:
        game.primary_deck = reconstruct_deck(game_state['primary_deck'])
    if 'played_primary' in game_state:
        game.played_primary = reconstruct_deck(game_state['played_primary'])
    if 'secondary_deck' in game_state:
        game.secondary_deck = reconstruct_deck(game_state['secondary_deck'])
    if 'played_secondary' in game_state:
        game.played_secondary = reconstruct_deck(game_state['played_secondary'])
    if 'judge' in game_state:
        game.judge = gamestate['judge']
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

    





# def state_to_dict(state):
#     game_state = {}
#     gamestate['players'] =

    # def play(self):
    #     ## Round loop
    #     #while 1:
    #     print("hello")

    # def do_turn_caller(player, state, do_turn_func):
    #     global state_change

    #     state_change = do_turn_func(player, state)

def check_for_interrupt(sock):
    sock.settimeout(0.01)
    try:
        data = recv_json(sock)
        if 'INTERRUPT' in data:
            return data['GAMESTATE']
        else:
            return None
    ## No interrupt was received!
    except socket.timeout:
        return None

#class Player:

#class PlayingCard:

c = CardGame()

c.set_config()

c.set_do_turn(do_turn)

c.set_init_state(init_state_bs)

c.set_draw_player(print_game)

c.run()
