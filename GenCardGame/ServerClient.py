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

inbox = []

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

    state.add_last_move()
    state.add_curr_rank(0)

    return state

def do_turn(game, player, index):
    """do turn BS"""

    game.curr_rank = game.curr_rank + 1
    if game.curr_rank > 13:
        game.curr_rank = 1

    print("which card(s) do you want to play?")

    num_cards = 0
    played = None

    game.add_last_move()

    while (num_cards < 4):
        num = input("number (1 - 13) or 'Q' to quit: ")
        if num == 'Q':
            break
        suit = input("suit (D, H, C, or S): ")
        card_to_play = PlayingCard((int(num), suit))
        played = game.players[index].hand.pick_card(card_to_play)
        if played == None:
            print("That card is not in your hand... try again:")
        else:
            game.add_card_on_table(played)
            game.add_to_last_move(played)
            num_cards += 1

    if played != None:
        message = ("%s played %d %s(s)" % (player.name, num_cards, game.get_curr_rank()))

    return game, message

def call_bs(game):

    called_bs = False
    call = input("Call BS? ('y'/'n'):")
    if call == 'y':
        called_bs = True

    return called_bs

def handle_bs(game, events):
    rank = game.curr_rank

    count = 0
    for player in game.players:
        if player.name == interupt_player.name:
            break;
        count += 1

    bs = False
    for card in game.last_move.cards:
        if card.number != game.curr_rank:
            bs = True

    message = ''

    if bs == True:
        message = ("BULLSHIT! cyprus takes cards")
        for card in game.last_move.cards:
            game.players[index].hand.add_card(card)
    else:
        message = ("NO BULLSHIT! %s takes cards" % player.name)
        for card in game.last_move.cards:
            game.players[count].hand.add_card(card)

    return game, message








def print_game(game, index):
    game.players[index].hand.print_hand_vertical()


# def get_next_player(game, index):
#     index += 1
#     if index == game.num_players:
#         index = 0
#     return index


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
        self.client_interrupt_func = None
        self.server_interrupt_func = None
        self.state                   = None

    def set_config(self,  
                   deck=standard_deck, secondary_deck=None, num_players=(2, 2), 
                   turn_order="inorder", interrupts=False, first_player=0, 
                   specialist_order="end"):
        # self.secondary_deck   = secondary_deck
        # self.turn_order       = turn_order
        # self.interrupts       = interrupts
        self.first_player     = first_player
        self.curr_player      = first_player
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

    def set_client_interrupt_handler(self, client_interrupt_func):
        self.client_interrupt_func = client_interrupt_func

    def set_server_interrupt_handler(self, server_interrupt_func):
        self.server_interrupt_func = server_interrupt_func

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
        global state_change
        ## Wait for signal that it is my turn

        interrupt, state, self.curr_player = wait_until_turn(self.name, self.parent_socket)

        game_state = reconstruct_state(state)

        ## I am the current player so I will look myself up
        player = None
        for p in game_state.players:
            if p.name == self.name:
                player = p
        
        ## An interrupt results in a none state until a new state is received
        if interrupt == None:
            called_bs = self.client_interrupt_func(game_state)
            if called_bs == True:
                print(player.get_json())
                send_json({'INTERRUPT_RUN': player.get_json(), 'NUM_PLAYER': self.curr_player}, self.parent_socket)
            return
        

        # player = list(filter(lambda p: p.name == self.name, game_state.players))

        ## Draw screen for client
        self.draw_player_func(game_state, self.curr_player)

        ## Spin off a thread to run the turn.  In the meanwhile we should be
        ## checking for an interrupt signal and the thread finishing
        self.stdin_thread = threading.Thread(target=do_turn_caller, \
                                             args=(game_state,   \
                                                   self.do_turn_func, self.parent_socket, player, self.curr_player))
        self.stdin_thread.start()


        #     ## If not interrupted check if we have finished our turn yet
        self.stdin_thread.join()

        # send_json({'TURN_DONE': self.curr_player}, self.parent_socket)

        # while True:
        #     data = recv_json(self.parent_socket)
        #     if "INTERRUPT" in data:
        #         return


        self.curr_player += 1
        if self.curr_player == len(game_state.players):
            self.curr_player = 0
        send_json({'NEXT_TURN': self.curr_player}, self.parent_socket)
        # take_messages.join()

    def start_server(self):
        ## Make game state

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


        [(name, connect, addr)] = child_connect

        state_data = self.state.get_json()

        send_json({'TURN':(first_name, self.curr_player), 'PLAYER_DATA': json.dumps(state_data)}, connect)

        ## Start loop to execute each round
        # count = 1
        # while True:
        #     if count == 1:
        #         send_json({'TURN':(first_name, self.curr_player), 'PLAYER_DATA': json.dumps(state_data)}, connect)
        #         # send_json({'msg': "hello"}, connect)
        #         count += 1

        for thread in monitor_threads:
            thread.join()

# player side           
def wait_until_turn(name, sock):
    while True:
        sock.settimeout(None)
        data = recv_json(sock)
        # print(data)
        if 'msg' in data:
            print(data['msg'])
        if 'SHUTDOWN' in data:
            print("Game shut down!  Exiting.")
            sys.exit(0)
        elif 'TURN' in data and data['TURN'][0] == name:
            return 1, data['PLAYER_DATA'], data['TURN'][1]
        elif 'INTERRUPT' in data:
            return None, data['INTERRUPT'], data['I_TURN']
        # print("END")

# player side
def do_turn_caller(game_state, do_turn, server_sock, player, index):
    global state_change
    state_change, message = do_turn(game_state, player, index)
    curr_state = state_change.get_json()
    send_json({'STATE_CHANGE': json.dumps(curr_state)}, \
                          server_sock)
    if message != '':
        send_json({'msg':message}, server_sock)

# server side
def update_state(child_sock, player_socks, server_interrupt_func):
    global state_change
    while True:
        data = recv_json(child_sock[1])
        if 'STATE_CHANGE' in data:
            new_data = data['STATE_CHANGE']
            new_state = reconstruct_state(new_data)
            state_lock.acquire()
            state_change = new_state
            state_lock.release()
        if 'msg' in data:
            inbox.append(data['msg'])
        if 'INTERRUPT_RUN' in data:
            interupt_player = data['INTERRUPT_RUN']
            cards = interupt_player['hand']
            points = interupt_player['points']
            name = interupt_player['name']
            hand = reconstruct_hand(cards)
            temp_player = Player(hand, name)
            temp_player.points = points
            curr_player = int(data['NUM_PLAYER'])
            new_state, message = server_interrupt_func(state_change, state_change.players[curr_player], curr_player, temp_player)
            state_lock.acquire()
            state_change = new_state
            state_lock.release()
            inbox.append(message)
        if 'NEXT_TURN' in data:
            state_lock.acquire()
            state_data = state_change.get_json()
            state_lock.release()
            num_next_player = data['NEXT_TURN']
            num_prev_player = num_next_player - 1
            if num_prev_player == 0:
                num_prev_player = 1
            for (name, conn, addr) in player_socks:
                if name == child_sock[0]:
                    continue;
                else:
                    send_json({'INTERRUPT':json.dumps(state_data), 'I_TURN': num_prev_player}, conn)
            state_lock.acquire()
            state_data = state_change.get_json()
            state_lock.release()
            send_json({'TURN': (state_change.players[num_next_player].name, num_next_player), 'PLAYER_DATA': json.dumps(state_data)}, \
                                    player_socks[num_next_player][1])



# server side
def handle_inbox(child_connects):
    while True:
        if len(inbox) != 0:
            m = inbox.pop(0)
            for (name, conn, addr) in child_connects:
                send_json({'msg':m}, conn)

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

# def check_for_interrupt(sock):
#     sock.settimeout(0.01)
#     try:
#         data = recv_json(sock)
#         if 'INTERRUPT' in data:
#             return data['GAMESTATE']
#         else:
#             return None
#     ## No interrupt was received!
#     except socket.timeout:
#         return None

#class Player:

#class PlayingCard:

c = CardGame()

c.set_config()

c.set_do_turn(do_turn)

c.set_init_state(init_state_bs)

c.set_draw_player(print_game)

c.set_client_interrupt_handler(call_bs)

c.set_server_interrupt_handler(handle_bs)

c.run()
