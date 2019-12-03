def num_to_type(num):
    x = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    return x[num - 1]

class PlayingCard:
    def __init__(self, face):
        number, suit = face
        if (number < 1 and number > 13):
            raise Exception("Invalid card number")
        if suit not in ['S', 'D', 'H', 'C']:
            raise Exception("Invalid suit")
        self.number = number
        self.suit = suit

    def rank_string(self):
        """returns rank of card as a string"""
        x = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King']
        return x[self.number - 1]
        return num

    def rank_num(self):
        """returns rank of card as its integer representation"""
        return self.number

    def same_rank(self, card):
        """return true if given card is of the same rank"""
        if self.rank == card.rank:
            return True
        else:
            return False

    def same_suit(self, card):
        """return true if given card is of the same suit"""
        if self.suit == card.suit:
            return True
        else:
            return False

    def is_equal(self, card):
        """return true if given card is of the same suit and rank"""
        if self.suit == card.suit and self.rank == card.rank:
            return True
        else: 
            return False

    def get_face(self):
        """returns card's face as well as width and height as a list of asciis to allow multiple card to be printed"""
        symbols = ['♠', '♦', '♥', '♣']
        symbol =''
        
        if self.suit == 'S':
            symbol = symbols[0]
        elif self.suit == 'D':
            symbol = symbols[1]
        elif self.suit == 'H':
            symbol = symbols[2]
        elif self.suit == 'C':
            symbol = symbols[3]

        number = num_to_type(self.number)

        if self.number in [1, 11, 12, 13]:
            spots = [6]
        elif self.number == 2:
            spots = [3, 9]
        elif self.number == 3:
            spots = [3, 6, 9]
        elif self.number == 4:
            spots = [2, 4, 8, 10]
        elif self.number == 5:
            spots = [2, 4, 6, 8, 10]
        elif self.number == 6:
            spots = [2, 4, 5, 7, 8, 10]
        elif self.number == 7:
            spots = [2, 4, 5, 6, 7, 8, 10]
        elif self.number == 8:
            spots = [2, 3, 4, 5, 7, 8, 9, 10]
        elif self.number == 9:
            spots = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        elif self.number == 10:
            spots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        if number != '10':
            temp_number = " " + number
        else:
            temp_number = '10'

        card_face = []
        card_face.append(temp_number)
        for i in range(1, 11):
            if i in spots:
                card_face.append(symbol)
            else:
                card_face.append(' ')

        if number != '10':
            temp_number = number + " "
        else:
            temp_number = '10'

        card_face.append(temp_number)

        card = """
┌─────────┐
│{}       │
│    {}    │
│ {}  {}  {} │
│ {}  {}  {} │
│ {}  {}  {} │
│         │
│       {}│
└─────────┘""".format(*card_face).split('\n')

        return 9, 11, card


    def print_card(self):
        """prints out ascii representation of a given card"""
        symbols = ['♠', '♦', '♥', '♣']
        symbol =''
        
        if self.suit == 'S':
            symbol = symbols[0]
        elif self.suit == 'D':
            symbol = symbols[1]
        elif self.suit == 'H':
            symbol = symbols[2]
        elif self.suit == 'C':
            symbol = symbols[3]

        number = num_to_type(self.number)

        if self.number in [1, 11, 12, 13]:
            spots = [6]
        elif self.number == 2:
            spots = [3, 9]
        elif self.number == 3:
            spots = [3, 6, 9]
        elif self.number == 4:
            spots = [2, 4, 8, 10]
        elif self.number == 5:
            spots = [2, 4, 6, 8, 10]
        elif self.number == 6:
            spots = [2, 4, 5, 7, 8, 10]
        elif self.number == 7:
            spots = [2, 4, 5, 6, 7, 8, 10]
        elif self.number == 8:
            spots = [2, 3, 4, 5, 7, 8, 9, 10]
        elif self.number == 9:
            spots = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        elif self.number == 10:
            spots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        if number != '10':
            temp_number = " " + number
        else:
            temp_number = '10'

        card_face = []
        card_face.append(temp_number)
        for i in range(1, 11):
            if i in spots:
                card_face.append(symbol)
            else:
                card_face.append(' ')

        if number != '10':
            temp_number = number + " "
        else:
            temp_number = '10'

        card_face.append(temp_number)

        card = """
┌─────────┐
│{}       │
│    {}    │
│ {}  {}  {} │
│ {}  {}  {} │
│ {}  {}  {} │
│         │
│       {}│
└─────────┘""".format(*card_face).split('\n')

        for i in range(10):
            print(card[i])



# print("Your hand: ")
# hand = []
# hand.append(PlayingCard(5, 'H'))
# hand.append(PlayingCard(8, 'S'))
# hand.append(PlayingCard(10, 'D'))
# hand.append(PlayingCard(12, 'C'))
# for card in hand:
#     card.print_card()