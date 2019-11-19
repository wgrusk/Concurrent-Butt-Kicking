import playerHandler

import threading
import json

class GameLogic:

    def __init__(self, players, story_file):
        self._players = players
        self._num_players = len(players)
        self._story = story_file

    def runGame(self):
        threads = []
        # Server Thread
        threads.append(threading.Thread(target=runServer, args=[]))

        # Client Threads
        for player in players:
            threads.append(threading.Thread(target=runPlayer, args=[player]))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def runPlayer(self, player):
        '''
        So essentially we want to run in a loop where the server thread assigns
        the current_story var to the next part of the story, then notifies the
        client threads that it's there. They all read it concurrently, and then
        pass that info onto their respective client handlers. Before the server
        thread notifies the client threads, it should start some sort of
        message waiting functionality where it waits for the responses from the
        clients. As respones come in, it should send them to the clients. It
        should keep a count so it knows when it's received its last response, 
        and should then begin the voting phase. One it's received all the votes,
        it'll send them to the clients to be printed. Then the loop will start
        over with the next portion of the story. If it reaches the end of the
        story, the server thread should signal the client threads by putting a
        flag (-1 or something) in the current story var. This will signify to
        the clients that the story is over, and the game as ended.
        '''