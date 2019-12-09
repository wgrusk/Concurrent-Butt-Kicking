#!/usr/bin/env python3
import sys, socket, json, select, threading
from GameClasses import *

PORT = 16390
state_change = None
state_lock = threading.Lock()
counter = 0

STANDARD_DECK = [(1, 'H'), (2, 'H'), (3, 'H'), (4, 'H'), (5, 'H'), (6, 'H'), 
                 (7, 'H'), (8, 'H'), (9, 'H'), (10, 'H'), (11, 'H'), (12, 'H'), 
                 (13, 'H'), (1, 'S'), (2, 'S'), (3, 'S'), (4, 'S'), (5, 'S'), 
                 (6, 'S'), (7, 'S'), (8, 'S'), (9, 'S'), (10, 'S'), (11, 'S'), 
                 (12, 'S'), (13, 'S'), (1, 'D'), (2, 'D'), (3, 'D'), (4, 'D'), 
                 (5, 'D'), (6, 'D'), (7, 'D'), (8, 'D'), (9, 'D'), (10, 'D'), 
                 (11, 'D'), (12, 'D'), (13, 'D'), (1, 'C'), (2, 'C'), (3, 'C'), 
                 (4, 'C'), (5, 'C'), (6, 'C'), (7, 'C'), (8, 'C'), (9, 'C'), 
                 (10, 'C'), (11, 'C'), (12, 'C'), (13, 'C')]

##################### UTILITY FUNCTIONS ######################################

# Format an int with the correct number of leading zeros for standard reading
def format_int(n):
    f = str(n)
    while len(f) < 9:
        f = str(0) + f
    return f

# Sends a json dict over the passed socket
def send_json(j, sock):
    jstr = json.dumps(j)
    msg_len = format_int(len(jstr))
    sock.send(msg_len.encode('utf-8'))
    sock.send(jstr.encode('utf-8'))

# Receives a json from the passed socket and returns it as a dict
def recv_json(sock):
    msg_len = int(sock.recv(9).decode('utf-8'))
    msg = json.loads(sock.recv(msg_len).decode('utf-8'))
    return msg

#############################################################################

class CardGame:
    ## TODO: client provided functions should be initialized to none so that
    ## we can check if they have been provided or not, and either execute
    ## them, skip (if possible), or crash (if we can't skip them)

    ## Classes that need updating:
    ## Event Class
    ## Client needs to include data structure to tell which do_turn function
    ## to run (sync or async)

    ## Functions we need:
    ## run_server()
    
    ## A class to represent game events
    class Event:
        def __init__(self, t, uid, c):
            self.type = t
            self.uid = uid
            self.closure = c

    ## A unique class used to terminate the message queue.  This way a user
    ## defined var will never be mistaken for the end of the queue
    class Terminator:
        def __init__(self):
            self.name = "Arnold"
            ## Your clothes... Give them to me. - Arnold

    def __init__(self):
        self.parent_socket = socket.socket()
        self.child_connections = []
        self.events = []
        self.messages = []
        self.message_lock = threading.Lock()
        self.message_cond = threading.Condition(self.message_lock)
        self.terminator = self.Terminator()

        self.min_players     = None
        self.max_players     = None
        self.init_state_func = None
        self.gamestate           = None
        self.win_check_flag  = False
        self.is_host         = False

    def set_num_players(self, num_players=(2,2)):
        self.min_players = num_players[0]
        self.max_players = num_players[1]

    def set_init_state(self, init_state_func):
        self.init_state_func = init_state_func

    ## Generate a unique id for each event using the counter
    def add_event(self, type, f):
        global counter

        self.events.append(self.Event(type, 
                                      'event_' + type + "_" + str(counter), 
                                      f))
        counter += 1

    def add_wincheck_event(self, f):
        self.add_event("win", f)
        self.win_check_flag = True

    def add_async_event(self, f):
        self.add_event("async", f)
    
    def add_sync_event(self, client_fun, server_fun, init_acc):
        self.add_event("sync", (client_fun, server_fun, init_acc))

    def add_next_turn(self, f):
        self.add_event("next", f)


    ## Asserts that the game is ready to run.  If not, exit.
    def ready_check(self):
        assert self.min_players and self.max_players, \
            "Error: Number of players not set! " + \
            "Call set_num_players((min, max)) to fix. Exiting!\n"
        assert self.events != [], \
            "Error: Event queue is empty! Add at least one event! Exiting!\n"
        assert self.init_state_func, \
            "Error: Missing init_state_function. " + \
            "Call set_init_state(init_state_func) to fix.  Exiting!\n"
        assert self.win_check_flag, \
            "Error: Win check is not used, game may not finish! " + \
            "Call add_wincheck_event(wincheck_func) to fix. Exiting!\n"

    def run(self):
        self.ready_check()
        
        if len(sys.argv) == 2 and sys.argv[1] == '-h':
            self.is_host = True
            self.setup_lobby()

            players = []
            for (name, sock, addr) in self.child_connections:
                players.append(Player(name))

            self.gamestate = self.init_state_func(GameState(players))

            self.run_server()
        elif len(sys.argv) == 4 and sys.argv[2] == '-c':
            self.is_host = False
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
                    send_json({'MSG': "Connected %s to the lobby\nThere are now"
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
                            send_json({'MSG':'disconnecting!', 'DC': 1}, conn)
                            conn.close()
                        sys.exit(0)
                    else:
                        ## Flush extra chars from line if they dont match
                        sys.stdin.readline()

        print("Let the games begin!")

        for (name, conn, addr) in self.child_connections:
            send_json({'MSG':'Starting the game!', 'START': 1}, conn)

    def run_server(self):
        winner = ""
        has_won = False

        while not has_won:
            for event in self.event_queue:
                if event.type is "async":
                    curr_player = self.gamestate.curr_player
                    curr_player_name = self.child_connections[curr_player][0]
                    for (name, sock, addr) in self.child_connections:
                        if name != curr_player_name:
                            send_json({'BROADCAST': "It's " + curr_player_name + "'s turn"}, sock)

                    send_json({'ASYNC': event.uid, 'STATE': json.dumps(self.gamestate.get_json())},  self.child_connections[curr_player][1])
                    data = recv_json(self.child_connections[curr_player][1])
                    if 'ASYNC_RESPONSE' in data:
                        self.gamestate = reconstruct_state(data['STATE'])
                elif event.type is "sync":
                    curr_player = self.gamestate.curr_player
                    curr_player_name = self.child_connections[curr_player][0]

                    init_acc = event.closure[2]
                    message_queue_fun = event.closure[1]

                    self.signal_sync_clients(event, curr_player_name)
                    self.gamestate = consume_message_queue(self.messages, self.message_lock,
                                                           self.message_cond, self, message_queue_fun,
                                                           init_acc, self.gamestate)
                elif event.type is 'next':
                    self.gamestate = event.closure(self.gamestate)

                elif event.type is "win":
                    has_won, winner = event.closure(self.gamestate)
                    if has_won:
                        break

        for (name, sock, addr) in self.child_connections:
            send_json({'BROADCAST': winner + " has won!!"}, sock)
            send_json({'STOP': " "}, sock)

        
    
    def broadcast(self, msg):
        assert self.is_host, "Only the server may call broadcast. Exiting\n"
        data = {'BROADCAST': str(msg)}
        for (name, conn, addr) in self.child_connections:
            send_json(data, conn)

    ## Run lobby on client side
    def setup_parent_connection(self):
        host_addr = sys.argv[3]
        self.name = sys.argv[1]
        
        self.parent_socket.connect((host_addr, PORT))
        send_json({'name': self.name}, self.parent_socket)
        
        while True:
            data = recv_json(self.parent_socket)
            
            if 'MSG' in data:
                print(data['MSG'])

            if 'DC' in data:
                self.parent_socket.close()
                break
            elif 'START' in data:
                self.start_client()
    
    def start_client(self):
        t = threading.Thread(target=client_message_loop, 
                             args=(self.parent_socket, self.messages, 
                                   self.message_lock, self.message_cond))
        t.start()
        self.run_client()
        t.join()
        sys.exit(0)

    def get_msg(self):
        with self.message_lock:
            if not self.messages:
                self.message_cond.wait()
            return self.messages.pop(0)

    def run_client(self):
        while True:
            data = self.get_msg()

            if 'SYNC' in data:
                event = [e for e in self.events if e.uid == data['SYNC']][0]
                fun = event.closure[0]
                gamestate = reconstruct_state(data['STATE'])
                response = fun(gamestate)
                #depending on what reponse is it might need to be converted to json
                send_json({'SYNC_RESPONSE' : json.dumps(response)}, self.parent_socket)

            # these kinda do same thing?
            if 'ASYNC' in data:
                event = [e for e in self.events if e.uid == data['ASYNC']][0]
                fun = event.closure
                #state needs to be passed
                gamestate = reconstruct_state(data['STATE'])
                new_state = fun(gamestate)
                send_json({'ASYNC_RESPONSE' : json.dumps(new_state.get_json())}, self.parent_socket)

            # probably need soemthing like this
            if 'STOP' in data:
                return

    def signal_sync_clients(self, event, curr_player_name):
        threads = []
        for (name, conn, addr) in self.child_connections:
            if name is not curr_player_name:
                t = threading.Thread(target=sync_thread,
                                     args=(conn, self.messages, self.message_lock, 
                                           self.message_cond, event.uid, name))
            t.start()
            threads.append(t)
        
        for thread in threads:
            thread.join()

        with self.message_lock:
            self.messages.append(self.terminator)

def client_message_loop(sock, messages, lock, cond):
    while True:
        data = recv_json(sock)

        ## Print broadcasts, don't pass them along
        if 'BROADCAST' in data:
            print(data['BROADCAST'])
        else:
            ## Put received message on message queue
            with lock:
                messages.append(data)
                cond.notify()
            ## Stop this thread if told to stop by server
            if 'STOP' in data:
                return

def send_client_sync(sock, gamestate):
    send_json({'SYNC': event.uid, 'STATE': json.dumps(self.gamestate.get_json())},  self.child_connections[curr_player][1])

# TODO
# We need to have the user specify the initial accumulator
def consume_message_queue(messages, queue_lock, queue_cond,
                          game, sync_fun, init_acc, curr_state):
    new_state = curr_state
    accumulator = init_acc
    while True:
        ## TODO: will this deadlock?  We never give up queue_lock...
        with queue_lock:
            if not messages:
                queue_cond.wait()
            message = messages.pop(0)
            
            if message is self.terminator:
                break
            new_state, accumulator = sync_fun(self,
                                              game,
                                              new_state,
                                              accumulator,
                                              message)

    return new_state



# Have to make sure that wherever queue_cond is initialized, it's initialized
# like this:
#
# queue_lock = threading.Lock()
# queue_cond = threading.Condition(queue_lock)
#
# ... or something like this.
def sync_thread(conn, messages, message_lock, message_cond, uid, name):
    send_json({'SYNC': uid}, conn)

    data = recv_json(conn)
    with message_lock:
        messages.append((name, data['SYNC_RESPONSE']))
        message_cond.notify()

# client side
# def do_turn_caller(game_state, do_turn, server_sock, player, index):
#     global state_change
#     state_change, message = do_turn(game_state, player, index)
#     curr_state = state_change.get_json()
#     send_json({'STATE_CHANGE': json.dumps(curr_state)}, \
#                           server_sock)
#     if message != '':
#         send_json({'msg':message}, server_sock)

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
    if 'curr_player' in game_state:
        game.curr_player = game_state['curr_player']
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
