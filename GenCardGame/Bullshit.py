#!/usr/bin/env python3

#import gencardgame

from Deck import Deck
from Hand import Hand
from Player import Player
from PlayingCard import PlayingCard

c = CardGame()

c.set_config()



c.run()

standard_deck = [(1, 'H'), (2, 'H'), (3, 'H'), (4, 'H'), (5, 'H'), (6, 'H'), 
                 (7, 'H'), (8, 'H'), (9, 'H'), (10, 'H'), (11, 'H'), (12, 'H'), 
                 (13, 'H'), (1, 'S'), (2, 'S'), (3, 'S'), (4, 'S'), (5, 'S'), 
                 (6, 'S'), (7, 'S'), (8, 'S'), (9, 'S'), (10, 'S'), (11, 'S'), 
                 (12, 'S'), (13, 'S'), (1, 'D'), (2, 'D'), (3, 'D'), (4, 'D'), 
                 (5, 'D'), (6, 'D'), (7, 'D'), (8, 'D'), (9, 'D'), (10, 'D'), 
                 (11, 'D'), (12, 'D'), (13, 'D'), (1, 'C'), (2, 'C'), (3, 'C'), 
                 (4, 'C'), (5, 'C'), (6, 'C'), (7, 'C'), (8, 'C'), (9, 'C'), 
                 (10, 'C'), (11, 'C'), (12, 'C'), (13, 'C')]

cards = []

for card in standard_deck:
    cards.append(PlayingCard(card))

deck1 = Deck(cards)

deck1.shuffle()

players = []

hands = deck1.divide_deck(5)

for hand in hands:
    players.append(Player(hand))

# for player in players:
#     print("your hand:")
#     player.hand.print_hand()

players[0].hand.print_hand()

print("which card do you want to play?")

num = input("number (1 - 13): ")
suit = input("suit (D, H, C, or S): ")

card_to_play = PlayingCard((int(num), suit))


played = players[0].hand.pick_card(card_to_play)

if played != None:
    print("player one played %s of %s" % (card_to_play.rank_string(), card_to_play.suit_string()))

players[0].hand.print_hand()    


