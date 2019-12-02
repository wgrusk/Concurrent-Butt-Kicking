class GameState:
	def __init__(self, players):
		self.players = players

	def add_primary_deck(self, deck):
		self.primary_deck = deck
		self.played_primary = Deck([])

	def add_secondary_deck(self, deck):
		self.secondary_deck = deck
		self.played_secondary = Deck([])

	def add_judge(self, player):
		self.judge = player