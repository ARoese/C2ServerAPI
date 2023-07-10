from src.serverRegister import Registration, serverBrowser
from src import a2s
from time import sleep

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL) #so that sigint will actually kill all threads

REMOTE = "http://127.0.0.1:8080"
#REMOTE = "https://servers.polehammer.net"

serverBrowser.getServerList(REMOTE)

with Registration(REMOTE) as re:
    for i in range(10):
        gameInfo = a2s.getInfo(("localhost",7071))
        re.updateMap(gameInfo.mapName)
        re.updatePlayercount(gameInfo.playerCount)
        re.updateMaxPlayercount(gameInfo.maxPlayers)
        sleep(5)
        print(serverBrowser.getServerList(REMOTE))

print("Server Ended")