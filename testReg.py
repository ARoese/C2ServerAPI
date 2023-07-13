from src.serverRegister import Registration, serverBrowser
from src import a2s
from time import sleep

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL) #so that sigint will actually kill all threads

##NOTE: Chivalry should be running locally for this test script to work. Otherwise, you should remove
##the a2s calls which will fail without an actual chivalry server running

##NOTE: Also, there should be a server list server running locally on port 8080

REMOTE = "http://127.0.0.1:8080"
#REMOTE = "https://servers.polehammer.net"

serverBrowser.getServerList(REMOTE)

with Registration(REMOTE, name="DrLong's awesome testing server", 
                  description="This server may or may or may not actually be live! Join at your own peril!",
                  gamePort=54432, queryPort=25565, pingPort=1234) as re:
        print(serverBrowser.getServerList(REMOTE))
        #while True:
        #    #gameInfo = a2s.getInfo(("localhost",7071))
        #    #re.updateMap(gameInfo.mapName)
        #    #re.updatePlayercount(gameInfo.playerCount+gameInfo.botCount)
        #    #re.updateMaxPlayercount(gameInfo.maxPlayers)
        #    print("Updated server information")
        #    sleep(10)
        sleep(5)

serverBrowser.getServerList(REMOTE)

print("Server Ended")