import random

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




