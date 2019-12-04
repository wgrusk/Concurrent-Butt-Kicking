from Hand import Hand

class Player:
    def __init__(self, cards, name='player'):
        self.hand = Hand(cards)
        self.points = 0
        self.name = name

    def get_json(self):
    	player_dict = {}
    	player_dict['hand'] = self.hand.get_json()
    	player_dict['points'] = self.points
    	player_dict['name'] = self.name
    	return player_dict