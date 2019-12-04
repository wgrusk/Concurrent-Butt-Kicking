from Deck import Deck

class GameState:
    def __init__(self, players):
        self.players = players
        self.cards_on_table = Deck([])
        self.primary_deck = None
        self.played_primary = None
        self.secondary_deck = None
        self.played_secondary = None
        self.judge = None

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

    def get_json(self):
        players = []
        for player in self.players:
            players.append(player.get_json())
        gamestate = {}
        gamestate['players'] = players
        gamestate['table_cards'] = self.cards_on_table.get_json()
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
        return gamestate

