import playerHandler

class GameLogic:

    def __init__(self, players, story_file):
        self.players = players
        self.num_players = len(players)
        self.story = story_file

    def runGame(self):
        
