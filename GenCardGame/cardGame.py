class CardGame:

    def __init__(self):
        self.parent_socket = socket.socket()

    def set_config(self, hand_size_init=5, deck=playing_cards,
                   num_players=(2, 2)):
        self.hand_size = hand_size_init
        self.deck = deck
        self.num_players = num_players

    def set_win_condition(has_won):
        self.win_condition = has_won

    def set_turn(do_turn):
        self.turn = do_turn

    def set_draw_player(draw_player):
        self.draw_player = draw_player

    def _assert_card_input(self, input):
        if type(input) is not str:
            return None

        input = input.split()

        if len(input) is not 2:
            return None
        try:
            rank = int(input[0])
        except:
            return None
        suit = input[1]
        return PlayingCard(rank, suit)


    def pick_a_card(self, prompt, player):
        hand = player.hand
        card = self._assert_card_input(input(prompt))
        while not card:
            card = self._assert_card(input("Can you even fucking read? You " + \
                                           "don't have that card, fuckwit. " + \
                                           "Try again."))
        return card

    def pick_a_player(self, player, state, prompt):
        player_names = [player.name for player in state]

        curr_player_name = player.name
        player_pick_name = input(prompt)
        while player_pick_name not in player_names or
              player_pick_name == curr_player_name:
            player_pick_name = input("That's not a player, dumbass. Try again.")
        player_pick = [player for player in state
                       if player.name == player_pick_name][0]
        return player_pick

    def card_in_hand(self, card, player):
        return True in [card.same_rank(hand_card) for hand_card in player.hand]

    def give_all_card_from_to(self, from_player, to_player, is_correct_card):
        from_hand = from_player.hand
        to_hand = to_player.hand

        num_taken = 0
        for card in from_hand:
            if is_correct_card(card):
                from_hand.remove(card)
                to_hand.append(card)
                num_taken += 1

        return num_taken
