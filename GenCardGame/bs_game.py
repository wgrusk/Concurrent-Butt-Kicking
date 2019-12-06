from GenCardGame import *

def init_state_bs(game):
    """initial BS state"""
    cards = []

    for card in standard_deck:
        cards.append(PlayingCard(card))

    deck1 = Deck(cards)

    deck1.shuffle()

    players = []

    hands = deck1.divide_deck(game.num_players)

    for i in range(game.num_players):
        players.append(Player(hands[i], game.player_names[i]))

    state = GameState(players)

    state.add_last_move()
    state.add_curr_rank(0)

    return state

def do_turn(game):
    """do turn BS"""

    game.curr_rank = game.curr_rank + 1
    if game.curr_rank > 13:
        game.curr_rank = 1

    game.players[game.curr_player].hand.print_hand_vertical()

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
    c = CardGame()
    c.set_config()
    c.set_init_state(init_state_bs)
    c.set_draw_player(print_game)
   
   
    ## Code for one turn-
    ## Async events only need client runnable code
    c.add_async_event(do_turn)
    ## Sync events needs client and server runnable
    c.add_sync_event(call_bs, handle_bs)
    
    c.add_wincheck_event(check_win) 
    
    c.run()

if __name__ == "__main__":
    main()
