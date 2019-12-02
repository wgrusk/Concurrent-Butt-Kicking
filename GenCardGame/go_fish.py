#!/usr/bin/env python3

import gencardgame
    
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

def pick_a_card(prompt, hand):
    num = input(prompt)

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

def card_is_in_hand(card, player, game):
    hand_nums = [num for (suit, num) in player.hand]
    game.broadcast(source=player, "%s" % ("Yes" if card in hand_nums else "No, go fish!"))
    return card in hand_nums

def num_to_str(num):
    x = ['ace', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'jack', 'queen', 'king']
    return x[num]

# takes current turn's player
def do_turn(curr_player, state, game):
    # Pick a card
    card_pick = game.pick_a_card("What card do you want to try and take?",
                                 curr_player)

    # Pick a player from which to try and take that card
    player_pick = game.pick_a_player(curr_player, state,
                                     "Who do you want to take it from?")

    card_pick_rank = card_pick.rank_string()
    game.broadcast("%s asks: do you have any %s's?" % (curr_player.name, card_pick_rank))

    if game.card_in_hand(card_pick, player_pick):
        correct_card = lambda card: card_pick.same_rank(card)
        num_taken = game.give_all_card_from_to(player_pick, curr_player, correct_card)

        game.broadcast("%s took %d %s's from %s!" % (curr_player.name,
                                                    num_taken,
                                                    card_pick_rank,
                                                    player_pick.name))







    ## Pick a card
    req_num = pick_a_card(curr_player.hand)

    ## Pick a player to ask for card
    p_target = game.get_player(pick_a_player(state))

    game.broadcast(source=curr_player, "Player %s do you have any %ss?", (p_target.name, num_to_str(req_num)))

    if card_is_in_hand(card_num, p_target):
        ## add the cards to curr_player, remove from p_target
        counter = 0
        for card in p_target.hand:
            if not card.number == req_num:
                continue
            game.remove_card(card, p_target)
            game.add_card(card, curr_player)
            counter += 1

        game.broadcast("%s took %d cards from %s" % (curr_player.name, counter, p_target.name))
        
        ## Check for 4 of a kind
        hand_nums = [num for (suit, num) in hand]
        for num in hand_nums:
            if hand_nums.count(num) == 4:
                game.broadcast(source=curr_player, "I have a book of 4 %ss!" % num_to_str(num))
                curr_player.hand = [card for card in curr_player.hand if card.numer != num]

        ## Take your turn again after a successful guess
        game.set_next_player(curr_player)
    ## go fish
    else:
        game.draw_card(curr_player)

def draw_player(player, state):
    for p in state['players']:
        if p.name == player.name:
            continue
        print("%s Hand: %s" % (p.name, "[]" * len(p.hand)))

    print("")
    print("Your hand has:")
    for card in player.hand:
        print("%s of %s", % (num_to_str(card.number), card.suit))

def mutate_state

def main():
    game = new CardGame()

    # default turn order=1,2,3,4..., default table_cards is 0, default interupts is false, default first player is P1
    game.set_config(hand_size_init=5, deck=GenCardGame.playing_cards, num_players=(2,4))
    game.set_win_condition(has_won)
    game.set_turn(do_turn, mutate_state)
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
