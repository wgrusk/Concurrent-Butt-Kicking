from Hand import Hand

class Player:
    def __init__(self, cards):
        self.hand = Hand(cards)
        self.points = 0