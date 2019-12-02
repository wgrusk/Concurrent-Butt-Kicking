#!/usr/bin/env python3

import gencardgame

class Card:
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit

## Client defined dict can hold data members that are not present in default player class
class Player:
    def __init__(self, name, extras):
        self.hand = []
        self.hand_size = 0
        self.score = 0
        self.name = name
        self.extras = extras
    
# returns player number who has won or None if the game is not over
def has_won(state):
    is_over = False
    for p in state['players']:
        if p.hand_size == 0:
            is_over = True

    max_score = 0
    winner = None
    if not is_over:
        for p in state['players']:
            if p.score > max_score:
                max_score = p.score
                winner = p.name

    return winner

def pick_a_card(hand):
    num = input("Pick the number of a card in your hand:")

    hand_nums = [num for (suit, num) in hand]

    while not num in hand_nums:
        num = input("You don't have a %s - try again:" % num)

    return num

def pick_a_player(state):
    name = input("Who do you want to take it from?")

    player_names = [player.name for player in state['players']]

    while not name in player_names:
        name = input("Player %s not found - try again:" % name)

    return name

def card_is_in_hand(card, player):
    hand_nums = [num for (suit, num) in player.hand]
    GenCardGame.broadcast(source=player, "%s" % ("Yes" if card in hand_nums else "No, go fish!"))
    return card in hand_nums

def num_to_str(num):
    x = ['ace', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'jack', 'queen', 'king']
    return x[num]

# takes current turn's player
def do_turn(curr_player, state):
    ## Pick a card
    req_num = pick_a_card(curr_player.hand)

    ## Pick a player to ask for card
    p_target = GenCardGame.get_player(pick_a_player(state))

    GenCardGame.broadcast(source=curr_player, "Player %s do you have any %ss?", (p_target.name, num_to_str(req_num)))

    if card_is_in_hand(card_num, p_target):
        ## add the cards to curr_player, remove from p_target
        counter = 0
        for card in p_target.hand:
            if not card.number == req_num:
                continue
            GenCardGame.remove_card(card, p_target)
            GenCardGame.add_card(card, curr_player)
            counter += 1

        GenCardGame.broadcast("%s took %d cards from %s" % (curr_player.name, counter, p_target.name))
        
        ## Check for 4 of a kind
        hand_nums = [num for (suit, num) in hand]
        for num in hand_nums:
            if hand_nums.count(num) == 4:
                GenCardGame.broadcast(source=curr_player, "I have a book of 4 %ss!" % num_to_str(num))
                curr_player.hand = list(filter(lambda card: card.number != num, curr_player.hand))

        ## Take your turn again after a successful guess
        GenCardGame.set_next_player(curr_player)


    ## go fish
    else:
        GenCardGame.draw_card(curr_player)

def draw_player(player, state):
    for p in state['players']:
        if p.name == player.name:
            continue
        print("%s Hand: %s" % (p.name, "[]" * len(p.hand)))

    print("")
    print("Your hand has:")
    for card in player.hand:
        print("%s of %s", %(num_to_str(card.number), card.suit))


def main():
    game = new CardGame();

    # default turn order=1,2,3,4..., default table_cards is 0, defualt interupts is false, default first player is P1
    game.set_config(hand_size_init=5, deck=GenCardGame.playing_cards, num_players=range(2,4))
    game.set_win_condition(has_won)
    game.set_turn(do_turn)
    game.set_player_extras(None)

    ## if not specified just print player info
    game.set_draw_player(draw_player)


    ## Game setup done
    """
    Turn sequence is:
    1) Draw state of curr player
    2) Do player turn
    3) Go to next player.
    """
    game.run()

if __name__ == "__main__":
    main()