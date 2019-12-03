import gencardgame

def winCondition(state):
    players = state.players
    for player in players:
        if len(player.hand) is 0:
            return True

    return False

def playerAction(curr_player, state):
    player = state.get_player(curr_player)
    cards_to_play = player.pick_from_hand("What cards do you want to put down?")

    table_deck = state.get_field("table_deck")
    table_deck.add_cards(cards_to_play)

    player_says = str(input("What do you want to say when you put them down?"))
    GenCardGame.broadcast(player_says)

    return state

def concurrentAction(curr_player, state):
    bs_or_pass = str(input("If you want to call BullShit, type anything! " + \
                           "If not, type 'pass'"))
    if bs_or_pass is "pass":
        return False
    else:
        return True

def main():
    bs = CardGame()
    

