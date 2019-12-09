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
        ## Connection to server/clients
        self.parent_socket = socket.socket()
        self.child_connections = []
        self.events = []
        
        ## Message queue and queue control
        self.messages     = []
        self.message_lock = threading.Lock()
        self.message_cond = threading.Condition(self.message_lock)
        self.terminator   = self.Terminator()

        ## Client-provided data/closures and metadata
        self.is_host         = False
        self.gamestate       = None
        self.min_players     = None
        self.max_players     = None
        self.win_check_flag  = False
        self.init_state_func = None

    def set_num_players(self, num_players=(2,2)):
        self.min_players = num_players[0]
        self.max_players = num_players[1]

    def set_init_state(self, init_state_func):
        self.init_state_func = init_state_func

    ## Game event and control flow functions generate a unique id for each event
    ## using the counter.  That ID is used to identify which closure to call 
    ## when the client is signaled.
    def add_event(self, t, f):
        global counter

        self.events.append(self.Event(t, 'event_' + t + "_" + str(counter), f))
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

    ## Runs the game.  Branches into client and server paths here
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
    
################################################################################
#                                                                              #
#                               Server Functions                               #
#                                                                              #
################################################################################
    
    ## Sets up and runs game waiting lobby, gets server ready to accept new TCP
    ## connections
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

            ## Try to accept a new TCP connection
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
                               % (name, self.num_players, 
                               ', '.join(self.player_names))},conn)
            ## Exception only if no new TCP connection this loop
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

    ## Runs main server loop, deal with events on event queue until a win-check
    ## event tells us that the game is over
    def run_server(self):
        global state_change

        winner = ""
        has_won = False

        while not has_won:
            for event in self.events:
                ## Handle triggering async events here
                if event.type is "async":
                    curr_player = self.gamestate.curr_player
                    curr_player_name = self.child_connections[curr_player][0]
                    for (name, sock, addr) in self.child_connections:
                        if name != curr_player_name:
                            send_json({'BROADCAST': "It's " + curr_player_name \
                                       + "'s turn"}, sock)

                    ## Trigger client to take turn and receive new state back
                    send_json({'ASYNC': event.uid, 
                               'STATE': json.dumps(self.gamestate.get_json())},
                               self.child_connections[curr_player][1])
                    data = recv_json(self.child_connections[curr_player][1])
                    
                    if 'ASYNC_RESPONSE' not in data:
                        print("ERROR: ASYNC_RESPONSE not received. Exiting")
                        sys.exit(1)
                    else:
                        self.gamestate = reconstruct_state(data['ASYNC_RESPONSE'])
                        for (name, sock, addr) in self.child_connections:
                            if name != curr_player_name:
                                send_json({'BROADCAST': data['MESSAGE']}, sock)

                ## Handle synchronous events
                elif event.type is "sync":
                    curr_player = self.gamestate.curr_player
                    curr_player_name = self.child_connections[curr_player][0]

                    init_acc = event.closure[2]
                    message_queue_fun = event.closure[1]

                    ## Concurrently consume the message queue
                    t = threading.Thread(target=CardGame.consume_message_queue,
                                         args=(self.messages, self.message_lock,
                                               self.message_cond, self, 
                                               message_queue_fun, init_acc, 
                                               self.gamestate, self.terminator))
                    t.start()

                    ## Populate message queue
                    self.signal_sync_clients(event, curr_player_name)
                    t.join()
                    
                    ## Flush message queue
                    self.messages = []

                    ## Get new gamestate from processing message queue
                    ## (effectively return value from thread)
                    self.gamestate = state_change
                     
                ## Calculate next player event 
                elif event.type is 'next':
                    self.gamestate = event.closure(self.gamestate)

                ## Check if someone won event
                elif event.type is "win":
                    has_won, winner = event.closure(self.gamestate)
                    if has_won:
                        break

        for (name, sock, addr) in self.child_connections:
            send_json({'BROADCAST': 
                       (winner.name + " has won!" if name != winner.name 
                       else "You win!")}, sock)
            send_json({'STOP': 1}, sock)

    ## Thread function to consume all messages on the message queue and 
    ## apply the user defined closure to them to modify the gamestate
    @staticmethod
    def consume_message_queue(messages, queue_lock, queue_cond,
                              game, sync_fun, init_acc, curr_state,
                              terminator):
        global state_change
        
        new_state = curr_state
        accumulator = init_acc
        
        while True:
            with queue_lock:
                if not messages:
                    queue_cond.wait()
                
                message = messages.pop(0)
                
                if message is terminator:
                    break
                
                new_state, accumulator = sync_fun(game, new_state, accumulator,
                                                  message)

        state_change = new_state
        
    ## Send a message to all clients
    def broadcast(self, msg):
        assert self.is_host, "Only the server may call broadcast. Exiting\n"
        data = {'BROADCAST': str(msg)}
        for (name, conn, addr) in self.child_connections:
            send_json(data, conn)

    ## Signal all clients to take an async turn and wait for replies.
    ## Multithreaded to take all messages concurrently
    def signal_sync_clients(self, event, curr_player_name):
        threads = []
        for (name, conn, addr) in self.child_connections:
            if name is not curr_player_name:
                t = threading.Thread(target=CardGame.sync_thread,
                                     args=(conn,self.messages,self.message_lock,
                                           self.message_cond, event.uid, name,
                                           self.gamestate))
                t.start()
                threads.append(t)
        
        for thread in threads:
            thread.join()

        ## After all messages are put onto the queue signal with terminator
        with self.message_lock:
            self.messages.append(self.terminator)
            self.message_cond.notify()

    ## Thread function that signals a client to take a synchronous turn then 
    ## waits for the result to come back.  When it receives a message it puts 
    ## that message on the message queue and signals the consumers of the 
    ## queue to process it
    @staticmethod
    def sync_thread(conn, messages, message_lock, message_cond, uid, name, 
                                                                     gamestate):
        send_json({'SYNC':uid, 'STATE':json.dumps(gamestate.get_json())}, conn)

        data = recv_json(conn)
        with message_lock:
            messages.append((name, data['SYNC_RESPONSE']))
            message_cond.notify()



################################################################################
#                                                                              #
#                               Client Functions                               #
#                                                                              #
################################################################################

    ## Run lobby on client side, waiting for game to start once it joins
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
    
    ## Start client loop; waiting to receive messages and executing closures
    ## when told by server
    def start_client(self):
        t = threading.Thread(target=CardGame.client_message_loop, 
                             args=(self.parent_socket, self.messages, 
                                   self.message_lock, self.message_cond))
        t.start()
        self.run_client()
        t.join()
        sys.exit(0)
    
    ## Take messages from the server in a seperate thread until told to stop,
    ## allows for blocking read on socket to not block execution of closures
    ## on client
    @staticmethod
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

    ## Consume client message queue
    def get_msg(self):
        with self.message_lock:
            if not self.messages:
                self.message_cond.wait()
            return self.messages.pop(0)

    ## Run client loop, getting messages off of message queue and running
    ## the appropriate closures
    def run_client(self):
        while True:
            data = self.get_msg()

            if 'SYNC' in data:
                event = [e for e in self.events if e.uid == data['SYNC']][0]
                fun = event.closure[0]
                gamestate = reconstruct_state(data['STATE'])
                response = fun(gamestate)
                
                ## Depending on the reponse might need to be converted to json
                send_json({'SYNC_RESPONSE' : response}, self.parent_socket)

            if 'ASYNC' in data:
                event = [e for e in self.events if e.uid == data['ASYNC']][0]
                #state needs to be passed
                gamestate = reconstruct_state(data['STATE'])
                new_state, message = event.closure(gamestate)
                send_json({'ASYNC_RESPONSE' : json.dumps(new_state.get_json()), 
                           'MESSAGE' : message}, self.parent_socket)

            if 'STOP' in data:
                return

################################################################################
#                                                                              #
#                        Game Data Classes & Functions                         #
#                                                                              #
################################################################################
 

class GameState:
    def __init__(self, players):
        self.players = players
        self.cards_on_table = Deck([])
        self.primary_deck = None
        self.played_primary = None
        self.secondary_deck = None
        self.played_secondary = None
        self.judge = None
        self.last_move = None
        self.curr_rank = None
        self.curr_player = 0

    def add_primary_deck(self, deck):
        """adds a primary deck of playing cards to game state
        which also adds a deck for played primary cards"""
        self.primary_deck = deck
        self.played_primary = Deck([])

    def add_secondary_deck(self, deck):
        """adds a secondary deck of playing cards to game state
        which also adds a deck for played secondary cards"""
        self.secondary_deck = deck
        self.played_secondary = Deck([])

    def add_judge(self, player):
        """adds a player as a judge to game state"""
        self.judge = player

    def add_card_on_table(self, card):
        """adds a given card to deck of cards on table"""
        self.cards_on_table.add_card(card)

    def add_last_move(self):
        self.last_move = Deck([])

    def add_to_last_move(self, card):
        self.last_move.add_card(card)

    def add_curr_rank(self, num):
        self.curr_rank = num

    def get_curr_rank(self):
        x = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return x[self.curr_rank]

    def add_to_last_move(self, card):
        self.last_move.add_card(card)

    def get_json(self):
        players = []
        for player in self.players:
            players.append(player.get_json())
        gamestate = {}
        gamestate['players'] = players
        gamestate['table_cards'] = self.cards_on_table.get_json()
        gamestate['curr_player'] = self.curr_player
        if self.primary_deck != None:
            gamestate['primary_deck'] = self.primary_deck.get_json()
        if self.played_primary != None:
            gamestate['played_primary'] = self.played_primary.get_json()
        if self.secondary_deck != None:
            gamestate['secondary_deck'] = self.secondary_deck.get_json()
        if self.played_secondary != None:
            gamestate['played_secondary'] = self.played_secondary.get_json()
        if self.judge != None:
            gamestate['judge'] = self.judge
        if self.curr_rank != None:
            gamestate['curr_rank'] = self.curr_rank
        if self.last_move != None:
            gamestate['last_move'] = self.last_move.get_json()
        return gamestate

## Turn a jsonified state back into a state object
def reconstruct_state(state):
    game_state = json.loads(state)
    players = []
    for player in game_state['players']:
        cards = player['hand']
        points = player['points']
        name = player['name']
        hand = reconstruct_hand(cards)
        temp_player = Player(name)
        temp_player.add_hand(hand)
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

class Player:
    def __init__(self, name):
        self.points = 0
        self.name = name

    def get_json(self):
        player_dict = {}
        player_dict['hand'] = self.hand.get_json()
        player_dict['points'] = self.points
        player_dict['name'] = self.name
        return player_dict

    def add_hand(self, cards):
        self.hand = Hand(cards)

class Deck:
    def __init__(self, cards):
        """takes a list of cards"""
        self.cards = cards

    def add_card(self, card):
        """adds a card to deck"""
        self.cards.append(card)

    def draw_card(self):
        """removes a card from top of deck"""
        return self.cards.pop()

    def shuffle(self):
        """shuffles deck"""
        random.shuffle(self.cards)

    def contains(self, card):
        """return true if given card is in deck"""
        if card in self.cards:
            return True
        else:
            return False

    def get_json(self):
        cards = []
        for card in self.cards:
            cards.append(card.get_json())
        return cards

    def add_deck(self, cards):
        """adds a list of cards to a deck"""
        self.cards.extend(cards)

    def divide_deck(self, num_players):
        """returns a list of lists of cards"""
        cards_per_hand = len(self.cards) // num_players
        hands = []
        for j in range(num_players):
            temp_hand = []
            for i in range(cards_per_hand):
                temp_hand.append(self.cards.pop())
            hands.append(temp_hand)

        for x in range(cards_per_hand):
            if len(self.cards) != 0:
                hands[x].append(self.cards.pop())
            else:
                break
        return hands

    def print_deck(self):
        """prints player's hand"""
        faces = []
        for card in self.cards:
            height, width, face = card.get_face()
            faces.append(face)

        lines = []
        for i in range(height):
            curr_line = []
            for j in range(len(self.cards)):
                curr_line.append(faces[j][i])
            lines.append(curr_line)

        for line in lines:
            print(" ".join(line))

    def to_string(self):

        faces = []
        for card in self.cards:
            height, width, face = card.get_face()
            faces.append(face)

        lines = []
        for i in range(height):
            curr_line = []
            for j in range(len(self.cards)):
                curr_line.append(faces[j][i])
            lines.append(curr_line)

        deck = ""
        for line in lines:
            deck += " ".join(line)
            deck += "\n"

        return deck

def reconstruct_deck(card_list):
    cards = []
    for card in card_list:
        cards.append(PlayingCard(card))
    return Deck(cards)

class Hand:
    def __init__(self, cards):
        self.cards = cards

    def add_card(self, card):
        """adds a card to hand"""
        self.cards.append(card)

    def pick_card(self, card):
        """if present in hand removes and returns given card, otherwise 
        returns none"""
        for i in range(len(self.cards)):
            if self.cards[i].is_equal(card):
                return self.cards.pop(i)
        return None

    def contains(self, card):
        """returns true if given card is in hand"""
        if card in self.cards:
            return True
        else:
            return False

    def pick_random_card(self):
        """removes and returns a random card from deck"""
        num_card = randint(range(len(self.cards)))
        return self.cards.pop(num_card)

    def size_hand(self):
        """gets size of hand"""
        return len(self.cards)

    def print_hand_vertical(self):
        """prints player's hand"""
        for card in self.cards:
            card.print_card()

    def get_json(self):
        cards = []
        for card in self.cards:
            cards.append(card.get_json())
        return cards

    def print_hand(self):
        """prints player's hand"""
        faces = []
        for card in self.cards:
            height, width, face = card.get_face()
            faces.append(face)

        lines = []
        for i in range(height):
            curr_line = []
            for j in range(len(self.cards)):
                curr_line.append(faces[j][i])
            lines.append(curr_line)

        for line in lines:
            print(" ".join(line))

    def to_string(self):
        faces = []
        for card in self.cards:
            height, width, face = card.get_face()
            faces.append(face)

        lines = []
        for i in range(height):
            curr_line = []
            for j in range(len(self.cards)):
                curr_line.append(faces[j][i])
            lines.append(curr_line)

        hand = ""
        for line in lines:
            hand += " ".join(line) 
            hand += "\n"

        return hand

def reconstruct_hand(card_list):
    cards = []
    for card in card_list:
        cards.append(PlayingCard(card))
    return cards

def num_to_type(num):
    x = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    return x[num - 1]

class PlayingCard:
    def __init__(self, face):
        number, suit = face
        if (number < 1 and number > 13):
            raise Exception("Invalid card number")
        if suit not in ['S', 'D', 'H', 'C']:
            raise Exception("Invalid suit")
        self.number = number
        self.suit = suit


    """returns rank of card as a string"""
    @staticmethod
    def rank_to_string(rank):
        x = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King']
        return x[rank - 1]

    def rank_string(self):
        return PlayingCard.rank_to_string(self.number)

    def suit_string(self):
        """returns rank of card as a string"""
        types = ['Hearts', 'Spades', 'Diamonds', 'Clubs']
        if self.suit == 'H':
            return 'Hearts'
        if self.suit == 'S':
            return 'Spades'
        if self.suit == 'D':
            return 'Diamonds'
        if self.suit == 'C':
            return 'Clubs'
        return None

    def rank_num(self):
        """returns rank of card as its integer representation"""
        return self.number

    def same_rank(self, card):
        """return true if given card is of the same rank"""
        if self.number == card.number:
            return True
        else:
            return False

    def same_suit(self, card):
        """return true if given card is of the same suit"""
        if self.suit == card.suit:
            return True
        else:
            return False

    def is_equal(self, card):
        """return true if given card is of the same suit and rank"""
        if self.suit == card.suit and self.number == card.number:
            return True
        else: 
            return False

    def get_json(self):
        return (self.number, self.suit)

    def get_face(self):
        """returns card's face as well as width and height as a list of asciis to allow multiple card to be printed"""
        symbols = ['♠', '♦', '♥', '♣']
        symbol =''
        
        if self.suit == 'S':
            symbol = symbols[0]
        elif self.suit == 'D':
            symbol = symbols[1]
        elif self.suit == 'H':
            symbol = symbols[2]
        elif self.suit == 'C':
            symbol = symbols[3]

        number = num_to_type(self.number)

        if self.number in [1, 11, 12, 13]:
            spots = [6]
        elif self.number == 2:
            spots = [3, 9]
        elif self.number == 3:
            spots = [3, 6, 9]
        elif self.number == 4:
            spots = [2, 4, 8, 10]
        elif self.number == 5:
            spots = [2, 4, 6, 8, 10]
        elif self.number == 6:
            spots = [2, 4, 5, 7, 8, 10]
        elif self.number == 7:
            spots = [2, 4, 5, 6, 7, 8, 10]
        elif self.number == 8:
            spots = [2, 3, 4, 5, 7, 8, 9, 10]
        elif self.number == 9:
            spots = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        elif self.number == 10:
            spots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        if number != '10':
            temp_number = " " + number
        else:
            temp_number = '10'

        card_face = []
        card_face.append(temp_number)
        for i in range(1, 11):
            if i in spots:
                card_face.append(symbol)
            else:
                card_face.append(' ')

        if number != '10':
            temp_number = number + " "
        else:
            temp_number = '10'

        card_face.append(temp_number)

        card = """
┌─────────┐
│{}       │
│    {}    │
│ {}  {}  {} │
│ {}  {}  {} │
│ {}  {}  {} │
│         │
│       {}│
└─────────┘""".format(*card_face).split('\n')

        return 10, 11, card


    def print_card(self):
        """prints out ascii representation of a given card"""
        symbols = ['♠', '♦', '♥', '♣']
        symbol =''
        
        if self.suit == 'S':
            symbol = symbols[0]
        elif self.suit == 'D':
            symbol = symbols[1]
        elif self.suit == 'H':
            symbol = symbols[2]
        elif self.suit == 'C':
            symbol = symbols[3]

        number = num_to_type(self.number)

        if self.number in [1, 11, 12, 13]:
            spots = [6]
        elif self.number == 2:
            spots = [3, 9]
        elif self.number == 3:
            spots = [3, 6, 9]
        elif self.number == 4:
            spots = [2, 4, 8, 10]
        elif self.number == 5:
            spots = [2, 4, 6, 8, 10]
        elif self.number == 6:
            spots = [2, 4, 5, 7, 8, 10]
        elif self.number == 7:
            spots = [2, 4, 5, 6, 7, 8, 10]
        elif self.number == 8:
            spots = [2, 3, 4, 5, 7, 8, 9, 10]
        elif self.number == 9:
            spots = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        elif self.number == 10:
            spots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        if number != '10':
            temp_number = " " + number
        else:
            temp_number = '10'

        card_face = []
        card_face.append(temp_number)
        for i in range(1, 11):
            if i in spots:
                card_face.append(symbol)
            else:
                card_face.append(' ')

        if number != '10':
            temp_number = number + " "
        else:
            temp_number = '10'

        card_face.append(temp_number)

        card = """
┌─────────┐
│{}       │
│    {}    │
│ {}  {}  {} │
│ {}  {}  {} │
│ {}  {}  {} │
│         │
│       {}│
└─────────┘""".format(*card_face).split('\n')

        for i in range(10):
            print(card[i])

class WordCard:
    def __init__(self, message):
        self.message = message

    def is_equal(self, card):
        """return true if given card has the same message"""
        if self.message == card.message:
            return True
        else: 
            return False


    def get_face(self):
        """returns card's face as well as width and height as a list of asciis to allow multiple card to be printed
        format = height, width, cardarray"""
        text = self.message

        card_face = []
        for i in range(0, 12):
            line = ''
            for i in range(0, 16):
                if len(text) != 0:
                    line += text[0]
                    text = text[1:]
                else:
                    break
            card_face.append(line)

        card = """
┌────────────────┐
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
└────────────────┘""".format(*card_face).split('\n')

        return 18, 15, card

    def print_card(self):
        """prints out ascii representation of a given card"""

        text = self.message

        card_face = []
        for i in range(0, 12):
            line = ''
            for i in range(0, 16):
                if len(text) != 0:
                    line += text[0]
                    text = text[1:]
                else:
                    break
            card_face.append(line)

        card = """
┌────────────────┐
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
│{:^16}│
└────────────────┘""".format(*card_face).split('\n')

        for i in range(15):
            print(card[i])
