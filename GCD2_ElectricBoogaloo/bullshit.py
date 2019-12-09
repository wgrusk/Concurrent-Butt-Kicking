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
    player = gamestate.players[gamestate.curr_player]

    gamestate.curr_rank = gamestate.curr_rank + 1
    if gamestate.curr_rank > 13:
        gamestate.curr_rank = 1

    print("It's your turn! This is your current hand:")

    player.hand.print_hand()

    print("Current rank is: %d" % gamestate.curr_rank)

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
        try:
            num = int(num)
        except:
            print("Please enter a valid number")
            continue
        if num < 1 or num > 13:
            print("Please enter a valid number")
            continue
        suit = input("Suit (D, H, C, or S): ")
        if (suit is not 'D' and
            suit is not 'H' and
            suit is not 'C' and
            suit is not 'S'):
            print("Please enter a valid suit")
            continue
        card_to_play = PlayingCard((num, suit))
        played = player.hand.pick_card(card_to_play)
        if played == None:
            print("That card is not in your hand... try again:")
        else:
            gamestate.add_card_on_table(played)
            gamestate.add_to_last_move(played)
            num_cards += 1

    message = input("What do you want to say when you put these cards down?\n")

    message = player.name + " said: " + message + "."

    return (gamestate, message)

def sync_turn_bs(gamestate):

    called_bs = False
    call = input("Call BS? ('y'/'n'):")
    if call == 'y':
        called_bs = True

    return called_bs

# Message is now tuple of player, and the message. Need this to broadcast who called
# bullshit.
def sync_handle_bs(game, gamestate, already_called, message):
    """accept first BS call"""

    bs_player_name, called_bs = message

    curr_player = gamestate.players[gamestate.curr_player]

    if (not already_called) and called_bs:

        game.broadcast("%s called Bullshit! Let's see what see what %s really played:" % (bs_player_name, curr_player.name))
        game.broadcast(gamestate.last_move.to_string())

        rank = gamestate.curr_rank

        lied = False
        for card in gamestate.last_move.cards:
            if card.number != gamestate.curr_rank:
                lied = True

        if lied:
            game.broadcast("Looks like they're full of shit! %s takes the cards" % curr_player.name)
            for card in gamestate.cards_on_table.cards:
                curr_player.hand.add_card(card)

            gamestate.cards_on_table.cards = []
        else:

            game.broadcast("Looks like they were telling the truth! %s takes cards" % bs_player_name)
            bs_player = None
            for player in gamestate.players:
                if player.name == bs_player_name:
                    bs_player = player

            for card in gamestate.last_move.cards:
                bs_player.hand.add_card(card)

        return (gamestate, True)
    else:
        return (gamestate, already_called)

def next_player_bs(gamestate):
    gamestate.curr_player = (gamestate.curr_player + 1) % len(gamestate.players)

    return gamestate


def main():

    # setting up game
    c = CardGame()
    c.set_num_players((3, 6))
    c.set_init_state(init_state_bs)

    # defining game logic
    c.add_async_event(async_turn_bs)
    c.add_sync_event(sync_turn_bs, sync_handle_bs, False)
    c.add_wincheck_event(win_cond_bs) 
    c.add_next_turn(next_player_bs)
    
    # running game
    c.run()

if __name__ == "__main__":
    main()
