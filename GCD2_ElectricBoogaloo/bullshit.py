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
    player = gamestate.players[game.curr_player]

    game.curr_rank = game.curr_rank + 1
    if game.curr_rank > 13:
        game.curr_rank = 1

    print("It's your turn! This is your current hand:")

    player.hand.print_hand()

    print("which card(s) do you want to put down?")

    num_cards = 0
    played = None

    gamestate.add_last_move()

    while (num_cards < 4):
        num = input("Number (1 - 13) or 'Q' to stop: ")
        if num == 'Q':
            if num_cards == 0:
                print("You must play at least 1 card")
                continue
            break
        suit = input("Suit (D, H, C, or S): ")
        card_to_play = PlayingCard((int(num), suit))
        played = player.hand.pick_card(card_to_play)
        if played == None:
            print("That card is not in your hand... try again:")
        else:
            gamestate.add_card_on_table(played)
            gamestate.add_to_last_move(played)
            num_cards += 1

    message = input("What do you want to say when you put these cards down?")

    message = player.name + " said: " + message + "."

    return (gamestate, message)

def sync_turn_bs(gamestate):
	"""call BS"""

    called_bs = False
    call = input("Call BS? ('y'/'n'):")
    if call == 'y':
        called_bs = True

    return called_bs

# Message is now tuple of player, and the message. Need this to broadcast who called
# bullshit.
def sync_handle_bs(game, gamestate, already_called, message):
	"""accept first BS call"""

    game.broadcast()

    if not already_called and message[1]:
        rank = gamestate.curr_rank

        lied = False
        for card in game.last_move.cards:
            if card.number != game.curr_rank:
                lied = True

        if lied == True:
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
    # c.set_win_cond(win_cond_bs)

    # defining game logic
    c.add_async_event(async_turn_bs)
    c.add_sync_event(sync_turn_bs, sync_handle_bs)



    ## Code for one turn-
    ## Async events only need client runnable code
    c.add_async_event(do_turn)
    ## Sync events needs client and server runnable
    c.add_sync_event(call_bs, handle_bs)
    
    c.add_wincheck_event(check_win) 
    
    c.run()

if __name__ == "__main__":
    main()
