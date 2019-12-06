from PlayingCard import PlayingCard

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

