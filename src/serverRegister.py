"""Code relating to registering servers with a server browser"""

from typing import AnyStr
from threading import Thread, Lock, Condition
import time

from . import serverBrowser

class Registration:
    """Represents a registration of this chivalry server with a server browser.
    
    This class automatically manages heartbeats and information-sharing with a chivalry server list.
        updates to this object (such as map/player count changes) are automatically sent to the
        server list specified in the constructor. Heartbeat signals are also sent periodically at
        the interval(s) requested by the server.
    """
    def __init__(self, serverListAddress, port: int = 7777, name: AnyStr = "Chivalry 2 Server", 
                   description: AnyStr = "No description", current_map: AnyStr = "Unknown", 
                   player_count: int = -1, max_players: int = -1, mods = []):
        """Constructor for the registration class

        :param serverListAddress: The URL of the serverlist to register with. This should be in the form 
            `http://0.0.0.0:8080`.
        :param port: The port on which the chivalry server is being hosted on.
        :param name: The name for this server that will be listed in the browser
        :param description: A description of the server that will be listed in the browser
        :param current_map: The current map of the chivalry server. This can be updated later.
        :param player_count: The number of players currently in the server
        :param max_players: The max number of players that can be in this server at once
        :param mods: TODO: UNIMPLEMENTED A list of mods that this server is running, that clients
            should download and install before joining.
        """
        #setup the mutex for this object
        self.__mutex = Lock()
        self.__current_map = current_map 
        self.__player_count = player_count
        self.__max_players=max_players
        self.serverListAddress=serverListAddress
        self.__stopHeartBeat = Condition()
        self.port = port
        #acquire the heartbeat mutex immediately, so that the heartBeat thread can never obtain it
        #until we release it in __stopHeartbeat()
        self.__stopHeartBeat.acquire()
        #register with the serverList
        self.__heartBeatThread = None
        self.unique_id, self.__key, self.refreshBy = serverBrowser.registerServer(self.serverListAddress, port, name, 
                   description, self.__current_map, self.__player_count, self.__max_players, mods)
        #start the heartbeat thread
        self.__heartBeatThread = Thread(target=self.__heartBeatThreadTarget)
        self.__heartBeatThread.start()

    def __pushUpdateToBackend(self):
        serverBrowser.updateServer(self.serverListAddress, 
                self.unique_id, self.__key, self.port, self.__player_count, 
                self.__max_players, self.__current_map)

    def updatePlayercount(self, player_count):
        """Update the number of players currently playing on the server

        This function will automatically push this update to the serverlist

        :param player_count: The new player count
        """
        with self.__mutex:
            self.__player_count = player_count
            self.__pushUpdateToBackend()

    def updateMaxPlayercount(self, max_players):
        """Update the max allowed number of players on the server
        
        This function will automatically push this update to the serverlist

        :param max_players: The new max number of players
        """
        with self.__mutex:
            self.__max_players = max_players
            self.__pushUpdateToBackend()

    def updateMap(self, current_map):
        """Update the current map the server is running
        
        This function will automatically push this update to the serverlist

        :param current_map: The new map
        """
        with self.__mutex:
            self.__current_map = current_map
            self.__pushUpdateToBackend()

    def stopHeartbeat(self):
        """Stop sending heartbeats to the server browser

        This effectively makes the object useless. It should not be called, but is made
            available in case it would be impractical to explicitly destroy the object.
            If you find yourself using this function, consider using `del`, or use the
            `with` language construct
        """
        #if the heartbeat thread exists
        if self.__heartBeatThread is not None and self.__heartBeatThread.is_alive():
            self.__stopHeartBeat.release()
            self.__heartBeatThread.join()
            self.__heartBeatThread = None
            self.__stopHeartBeat.acquire()

    def __doHeartBeat(self):
        if self.__heartBeatThread is None:
            return
        with self.__mutex:
            print("Heartbeat")
            self.refreshBy = serverBrowser.heartbeat(self.serverListAddress, self.unique_id, self.__key, self.port)

    def __heartBeatThreadTarget(self):
        print("Heartbeat thread started")
        while True:
            #this will wait for a shutdown signal until it's time for the next heartbeat
            #when that time elapses, then do a heartbeat and go back to waiting
            #this way, a shutdown signal can be sent at basically any time
            #and be handled immediately, the thread is always asleep otherwise,
            #and only ever wakes up when it actually has something to do.

            #this will always sent a heartbeat 20% of the way before expiry, to give wiggle-room
            if not self.__stopHeartBeat.acquire(timeout=0.8*(self.refreshBy - time.time())):
                self.__doHeartBeat()
            else:
                print("Heartbeat thread ended")
                self.__stopHeartBeat.release()
                return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stopHeartbeat()
        #if exc_tb is not None:
        #    traceback.print_tb(exc_tb)
            
    def __del__(self):
        self.stopHeartbeat()