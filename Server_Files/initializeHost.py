import gameLogic
import playerHandler

STORYFILE = "./story.txt"

class InitializeHost:

    def __init__(self, hostIP):
        self._hostIP = hostIP


    def create_lobby_run_game(self):
        print("The game lobby IP is:" + self._hostIP)
        print("As other players join, their names will show up here.")
        print("Please type 'start' when you're ready to start the game.")

        players = get_players()
        start_game(players)


    def get_players(self):
        '''
        Listen for new connections, and for each new IP, create a playerHandler
        for them. When the user types 'start', stop listening for connections,
        and return the list of playerHandlers.
        '''


    def start_game(self, players):
        game = gameLogic.GameLogic(players, STORYFILE)
        game.run_game()
