from src.serverRegister import Registration, serverBrowser
from src import a2s
from time import sleep

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL) #so that sigint will actually kill all threads

#REMOTE = "http://127.0.0.1:8080"
REMOTE = "https://servers.polehammer.net"

print(serverBrowser.getServerList(REMOTE))