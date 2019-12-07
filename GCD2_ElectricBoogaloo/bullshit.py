from GameClasses import *
from ServerClient import *


def init_state_bs(gamestate):
    """initial BS state"""

    # initialize cards
    cards = []
    for card in STANDARD_DECK:
        cards.append(PlayingCard(card))

    deck1 = Deck(cards)
    deck1.shuffle()
    hands = deck1.divide_deck(len(gamestate.players))

    # initilaize players
    for i, player in enumerate(gamestate.players):
        player.add_hand(hands[i])

    # initilaize state fields that we will need
    gamestate.add_last_move()
    gamestate.add_curr_rank(0)

    return gamestate

def win_cond_bs(gamestate):
    """check win condition for BS"""
    for player in gamestate.players:
        if player.hand.size_hand() == 0:
            return (True, player)
    return (False, None)

def async_turn_bs(gamestate):
    """do turn BS"""

    game.curr_rank = game.curr_rank + 1
    if game.curr_rank > 13:
        game.curr_rank = 1

    print()

    game.players[game.curr_player].hand.print_hand()

    print("which card(s) do you want to play?")

    num_cards = 0
    played = None

    game.add_last_move()

    while (num_cards < 4):
        num = input("number (1 - 13) or 'Q' to quit: ")
        if num == 'Q':
            break
        suit = input("suit (D, H, C, or S): ")
        card_to_play = PlayingCard((int(num), suit))
        played = game.players[game.curr_player].hand.pick_card(card_to_play)
        if played == None:
            print("That card is not in your hand... try again:")
        else:
            game.add_card_on_table(played)
            game.add_to_last_move(played)
            num_cards += 1

    if played != None:
        message = ("%s played %d %s(s)" % (game.players[game.curr_player].name, \
        									num_cards, game.get_curr_rank()))

    return game, message

def call_bs(game, index):
	"""call BS"""

    called_bs = False
    call = input("Call BS? ('y'/'n'):")
    if call == 'y':
        called_bs = True

    return game, message

def handle_bs(gamestate, messages):
	"""accept first BS call"""
	for m in messages:
		if message != '':
			return game, message
    message = ''

    if called_bs == True:
        rank = game.curr_rank

        bs = False
        for card in game.last_move.cards:
            if card.number != game.curr_rank:
                bs = True

        if bs == True:
            message = ("BULLSHIT! %s takes cards" % game.players[game.curr_player].name)
            for card in game.last_move.cards:
                game.players[game.curr_player].hand.add_card(card)
        else:
            message = ("NO BULLSHIT! %s takes cards" % game.players[index].name)
            for card in game.last_move.cards:
                game.players[index].hand.add_card(card)

    game.curr_player += 1
    if game.curr_player == len(game.players):
        game.curr_player = 0

def print_game(game, index):
    game.players[index].hand.print_hand_vertical()

def main():

    # setting up game
    c = CardGame()
    c.set_num_players((4, 6))
    c.set_init_state(init_state_bs)
    c.set_win_cond(win_cond_bs)

    # defining game logic
    c.add_async_event(async_turn_bs)




    ## Code for one turn-
    ## Async events only need client runnable code
    c.add_async_event(do_turn)
    ## Sync events needs client and server runnable
    c.add_sync_event(call_bs, handle_bs)
    
    c.add_wincheck_event(check_win) 
    
    c.run()

if __name__ == "__main__":
    main()
