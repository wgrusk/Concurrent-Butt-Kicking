import serverHandler
import socket 

# hostname = socket.gethostname()    
# IPAddr = socket.gethostbyname(hostname) 

class ClientLogic:

	# This is just a rough, small outline. Feel free to change whatever.
	def __init__(self, server_IP):
		self.serverConnection = ServerHandler(server_IP)
		#self.screen = Client_IO()

	def join_waiting_room(self):
		print("hello")
		self.serverConnection.join()
		# is function different if client is first one to join?

	def monitor_game(self, game):
		# get scene
		# send vote
		# send 

	def run_game(self):
		# get story from server connection 
		pygame.init()
		game = gameScreen(["scene 1", "scene 2"])
		monitor = threading.Thread(target=monitor_game, args=(game, ))
		monitor.start()
		game.run()
		monitor.join()
		pygame.quit()

	# start up game with welcome window 



game = ClientLogic()
game.run_game()
