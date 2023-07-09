from src.serverRegister import Registration, serverBrowser
from time import sleep

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL) #so that sigint will actually kill all threads

REMOTE = "http://127.0.0.1:8080"
#REMOTE = "https://servers.polehammer.net"

serverBrowser.getServerList(REMOTE)

with Registration(REMOTE) as re:
    for i in range(10):
        re.updateMap(str(i))
        sleep(5)
        print(serverBrowser.getServerList(REMOTE))

print("Server Ended")