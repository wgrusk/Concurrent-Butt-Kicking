from Deck.py import Deck

class GameState:
    def __init__(self, players):
        self.players = players
        self.cards_on_table = Deck([])

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