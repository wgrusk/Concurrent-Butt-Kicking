import serverHandler
import clientLogic

class InitializePlayer:

    def __init__(self, playerIP):
        self._playerIP = playerIP


    def join_lobby_run_game(self, hostIP):
        host = connect_to_host(hostIP)
        start_game(host)


    def connect_to_host(self, hostIP):
        '''
        Connect to hostIP and send self._playerIP (along with port #?). If
        successful, create serverHandler with hostIP and return it.
        '''


    def start_game(self, host):
        game = clientLogic.ClientLogic(host)
        game.run_game()
