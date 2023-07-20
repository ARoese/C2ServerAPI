from src.serverRegister import Registration, serverBrowser
from src import a2s
from time import sleep
import argparse

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL) #so that sigint will actually kill all threads

##NOTE: Chivalry should be running locally for this test script to work. Otherwise, you should remove
##the a2s calls which will fail without an actual chivalry server running

##NOTE: Also, there should be a server list server running locally on port 8080

#REMOTE = "http://127.0.0.1:8080"

args = argparse.ArgumentParser(description="Register a Chivalry 2 server with the server browser")
args.add_argument('-r', "--remote", required=False, type=str, default="http://servers.polehammer.net")
args.add_argument('-n', "--name", required=False, type=str, default="Chivalry 2 Private Server")
args.add_argument('-d', "--description", required=False, type=str, default="")
args = args.parse_args()

serverBrowser.getServerList(args.remote)

with Registration(args.remote, name=args.name, description=args.description) as re:
    print(serverBrowser.getServerList(args.remote))
    while True:
        try: 
            gameInfo = a2s.getInfo(("localhost",re.queryPort))
            re.updateMap(gameInfo.mapName)
            re.updatePlayercount(gameInfo.playerCount+gameInfo.botCount)
            re.updateMaxPlayercount(gameInfo.maxPlayers)
            print(f"Updated server information successfully. Players: {gameInfo.playerCount} Bots: {gameInfo.botCount} Map: {gameInfo.mapName}")
            sleep(10)
        except ConnectionResetError:
            print("Connection reset. Trying again.")
            sleep(1)
        except Exception as e:
            print("Something went wrong. Trying again.")
            print(e.with_traceback(None))
            sleep(1)