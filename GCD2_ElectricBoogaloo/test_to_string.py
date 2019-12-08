from GameClasses import *
from ServerClient import *

cards = []
for card in STANDARD_DECK:
    cards.append(PlayingCard(card))

hand = Hand(cards[:3])

print(hand.to_string())
