#!/usr/bin/env python3

import gencardgame

# once someone reaches 5 points they win
def has_won(state):
    is_over = False
    winner = None
    for p in state['players']:
        if p.points == 5:
            winner = p.name
            is_over = True

    return winner

# draw card from deck
def draw_card(deck):
    return deck.pop()

def start_round(state):
    # judge draws black card
    black_card = state.secondary_deck.draw_card()

    # "reads" card to players
    GenCardGame.broadcast("The prompt is: %s" % black_card.message)


# conduct round of game
def do_turn(curr_player, state, game):

    if state.judge != curr_player.name:

        response = pick_a_card("Pick a card to answer the prompt: ", curr_player.hand)
        game.send_choice(response);

        # waits for responses
        responses = []
        responses = game.get_responses()

        # print responses to all users
        game.broadcast_fun(print_responses(responses))

        # could this return a player instead of a name
        winner = pick_a_player

        game.broadcast("The winner is: %s" % winner.name)

        # function to add points
        winner.add_points(1)

        # function to 

def mutate_state(curr_player, state, game):


def do_judge(state):
    # judge draws black card
    winner = pick_a_card(prompt, state.table_cards)

    # "reads" card to players
    game.broadcast("The winner is: %s" % winner.name)


def main():
    game = new CardGame();

    white_cards = []
    black_cards = []

    # default turn order=1,2,3,4..., default table_cards is 0, defualt interupts is false, default first_player is P1
    game.set_config(hand_size_init=10, deck=white_cards, secondary_deck=black_cards, num_players=(3,8), turn_order='barrier')
    game.set_win_condition(has_won)
    game.set_round_start(do_start, update_start)
    game.set_turn(do_turn, update_turn)
    game.set_specialist_turn(do_judge, update_judge)
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


