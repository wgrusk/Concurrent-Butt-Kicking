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



# print("Your hand: ")
# hand = []
# hand.append(WordCard('I drink because ____________.'))
# hand.append(WordCard('Concurrency'))
# for card in hand:
#     card.print_card()