import sys
sys.path.append('../GenCardGame')

from PlayingCard import PlayingCard
from Hand import Hand

def main():
    #screenOne()
    #screenOneA()
    #screenTwo()
    #screenThree()
    screenFour()

def screenOne():
    cards = [(2, 'H'), (11, 'C'), (7, 'S'), (13, 'S')]
    for i, card in enumerate(cards):
        cards[i] = PlayingCard(card)

    hand = Hand(cards)
    for i in range(30):
        print("\n")
    print("It's your turn! This is your current hand:")
    hand.print_hand()
    cards = input("Which cards do you want to put down?\n")
    speech = input("What do you want to say when you put those cards down?\n")

def screenOneA():
    for i in range(31):
        print("\n")
    print("It's 'Jake's turn. Let's see what they say.\n\n")

def screenTwo():
    for i in range(31):
        print("\n")
    bs_pass = input("'Jake' said 'Two Sevens'. Type 'Bullshit!' to call " + \
                    "Bullshit or 'Pass' otherwise.\n")

def screenThree():
    for i in range(31):
        print("\n")
    cards = [(2, 'H'), (7, 'S')]
    for i, card in enumerate(cards):
        cards[i] = PlayingCard(card)

    hand = Hand(cards)
    print("'Johanna' called Bullshit! Let's see what 'Jake' really played:")
    hand.print_hand()
    print("Looks like they're full of shit! " + \
          "'Jake' has to pick up the whole deck!\n\n")

def screenFour():
    for i in range(31):
        print("\n")
    cards = [(2, 'H'), (11, 'C'), (7, 'S'), (13, 'S'), (1, 'D'), (4, 'C'),
             (13, 'H'), (9, 'D'), (4, 'D')]
    for i, card in enumerate(cards):
        cards[i] = PlayingCard(card)

    hand = Hand(cards)
    print("This is your new hand:")
    hand.print_hand()
    print("\n\n")

if __name__ == "__main__":
    main()
