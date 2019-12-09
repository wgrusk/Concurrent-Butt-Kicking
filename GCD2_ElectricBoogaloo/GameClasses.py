import random

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

    def rank_string(self):
        """returns rank of card as a string"""
        x = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King']
        return x[self.number - 1]
        return num

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
