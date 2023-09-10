"""Code relating to registering servers with a server browser"""

from typing import AnyStr
from threading import Thread, Lock, Condition
import time
import a2s

import serverBrowser

MAX_RETRIES = 10
class Registration:
    """Represents a registration of this chivalry server with a server browser.
    
    This class automatically manages heartbeats and information-sharing with a chivalry server list.
        updates to this object (such as map/player count changes) are automatically sent to the
        server list specified in the constructor. Heartbeat signals are also sent periodically at
        the interval(s) requested by the server.
    """
    def __init__(self, serverListAddress, gamePort: int = 7777, pingPort: int = 3075, queryPort: int = 7071, 
                    name: AnyStr = "Chivalry 2 Server", description: AnyStr = "No description",
                    current_map: AnyStr = "Unknown", 
                    player_count: int = -1, max_players: int = -1, mods = [], printLambda=print):
        """Constructor for the registration class

        @param serverListAddress: The URL of the serverlist to register with. This should be in the form 
            `http://0.0.0.0:8080`.
        @param gamePort: The UDP port on which the chivalry server is being hosted on.
        @param pingPort: The UDP port (usually in the range 30xx) which the chivalry server responds to pings on
        @param queryPort: The UDP port which responds to A2S, (A steam protocol) usually 7071
        @param name: The name for this server that will be listed in the browser
        @param description: A description of the server that will be listed in the browser
        @param current_map: The current map of the chivalry server. This can be updated later.
        @param player_count: The number of players currently in the server
        @param max_players: The max number of players that can be in this server at once
        @param mods: TODO: UNIMPLEMENTED A list of mods that this server is running, that clients
            should download and install before joining.
        @param printLambda: A function of the form `printLambda(str) -> None` that should be called in order to 
            present any sort of output to the user. Defaults to print, sending output to stdout. If you're using
            curses, make a lambda that sends the string to whatever output window you're using.
        """
        #setup the mutex for this object
        self.__mutex = Lock()
        self.serverListAddress=serverListAddress
        self.__stopHeartbeatCond = Condition()
        self.__stopUpdateCond = Condition()
        self.port = gamePort
        self.queryPort = queryPort
        self.pingPort = pingPort
        self.name = name
        self.description = description
        self.mods = mods
        self.a2sInfo : a2s.A2S_INFO = a2s.A2S_INFO()
        self.__heartBeatThread = None
        self.__updateThread = None
        self.__printLambda = printLambda

    def __pushUpdateToBackend(self):
        serverBrowser.updateServer(self.serverListAddress, 
                self.unique_id, self.__key, self.a2sInfo.playerCount, 
                self.a2sInfo.maxPlayers, self.a2sInfo.mapName)
        self.__printLambda("Updated server information successfully.\n"
                           + f"\tPlayers: {self.a2sInfo.playerCount}\n"
                           + f"\tmaxPlayers: {self.a2sInfo.maxPlayers}\n"
                           + f"\tBots: {self.a2sInfo.botCount}\n"
                           + f"\tMap: {self.a2sInfo.mapName}\n")

    def __doUpdate(self):
        tries = 0
        info : a2s.A2S_INFO = a2s.A2S_INFO()
        while tries < MAX_RETRIES:
            try:
                info = a2s.getInfo()
            except:
                tries += 1
                self.__printLambda(f"a2s timed out. Trying again ({tries}/{MAX_RETRIES})")
                time.sleep(1)
        with self.__mutex:
            if info != self.a2sInfo:
                self.a2sInfo = info
                self.__pushUpdateToBackend()

    def __startHeartbeat(self):
        #acquire the heartbeat mutex immediately, so that the heartBeat thread can never obtain it
        #until we release it in __stopHeartbeat()
        self.__stopHeartbeatCond.acquire()
        #start the heartbeat thread
        self.__heartBeatThread = Thread(target=self.__heartBeatThreadTarget)
        self.__heartBeatThread.start()

    def __stopHeartbeat(self):
        #if the heartbeat thread exists
        if self.__heartBeatThread is not None and self.__heartBeatThread.is_alive():
            self.__stopHeartbeatCond.release()
            self.__heartBeatThread.join()
            self.__heartBeatThread = None
            self.__stopHeartbeatCond.acquire()

    def __startUpdating(self):
        #acquire the update mutex immediately, so that the thread can never obtain it
        #until we release it in __stopUpdating()
        self.__stopUpdateCond.acquire()
        #start the update thread
        self.__updateThread = Thread(target=self.__updateThreadTarget)
        self.__updateThread.start()

    def __stopUpdating(self):
        if self.__updateThread is not None and self.__updateThread.is_alive():
            self.__stopUpdateCond.release()
            self.__updateThread.join()
            self.__updateThread = None
            self.__stopUpdateCond.acquire()

    def __doHeartBeat(self):
        if self.__heartBeatThread is None:
            return
        with self.__mutex:
            self.refreshBy = serverBrowser.heartbeat(self.serverListAddress, self.unique_id, self.__key, self.port)
            self.__printLambda("Heartbeat signal sent to server list")

    def __heartBeatThreadTarget(self):
        self.__printLambda("Heartbeat thread started")
        while True:
            #this will wait for a shutdown signal until it's time for the next heartbeat
            #when that time elapses, then do a heartbeat and go back to waiting
            #this way, a shutdown signal can be sent at basically any time
            #and be handled immediately, the thread is always asleep otherwise,
            #and only ever wakes up when it actually has something to do.

            #this will always sent a heartbeat 20% of the way before expiry, to give wiggle-room
            try:
                self.__printLambda(str((self.refreshBy - time.time())))
                if not self.__stopHeartbeatCond.acquire(timeout=0.8*(self.refreshBy - time.time())):
                    self.__doHeartBeat()
                else:
                    self.__printLambda("Heartbeat thread ended")
                    self.__stopHeartbeatCond.release()
                    return
            except Exception as e:
                self.__printLambda("Failed to send heartbeat to the server list:")
                self.__printLambda(str(e))
                time.sleep(1)
    
    def __updateThreadTarget(self):
        self.__printLambda("Update thread started")
        while True:
            try:
                if not self.__stopUpdateCond.acquire(timeout=1):
                    self.__doUpdate()
                else:
                    self.__printLambda("Update thread ended")
                    self.__stopUpdateCond.release()
                    return
            except Exception as e:
                self.__printLambda("Failed to send update to the server list:")
                self.__printLambda(str(e))
                time.sleep(1)

    def __enter__(self):
        #register with the serverList
        self.unique_id, self.__key, self.refreshBy = serverBrowser.registerServer(self.serverListAddress, 
                    self.port, self.pingPort, self.queryPort, self.name, 
                    self.description, self.a2sInfo.mapName, self.a2sInfo.playerCount, self.a2sInfo.maxPlayers, self.mods)
        self.__startHeartbeat()
        self.__startUpdating()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__stopHeartbeat()
        self.__stopUpdating()
        serverBrowser.delete(self.serverListAddress, self.unique_id, self.__key)
            
    def __del__(self):
        self.__stopHeartbeat()
        self.__stopUpdating()