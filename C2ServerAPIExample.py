from C2ServerAPI.guiServer import Chivalry
from time import sleep

game = Chivalry() #attach to the game window

game.openConsole()

if game.isMainMenu():
    game.consoleSend("open ffa_courtyard?listen")
else:
    game.consoleSend("servertravel ffa_courtyard")

sleep(30) #wait for the game to load

while not game.isGameEnd():
    game.closeConsole()
    #the y here at the start is required to open the chat box
    game.consoleSend("yThis is a test message to be sent in game chat by the server every 5 seconds!")
    game.openConsole()
    sleep(5)