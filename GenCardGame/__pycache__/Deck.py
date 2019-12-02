import random

class Deck:
	def __init__(self, cards):
		self.cards = cards

	def add_card(self, card):
		self.cards.append(card)

	def draw_card(self, card):
		return self.cards.pop(card)

	def shuffle(self):
		random.shuffle(self.cards)
