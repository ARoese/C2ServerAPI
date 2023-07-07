"""Code relating to registering servers with a server browser"""

from typing import AnyStr
from threading import Thread, Lock, Condition
import time

from . import serverBrowser

class Registration:
    def __init__(self, serverListAddress, port: int = 7777, name: AnyStr = "Chivalry 2 Server", 
                   description: AnyStr = "No description", current_map: AnyStr = "Unknown", 
                   player_count: int = -1, max_players: int = -1, mods = []):
        #setup the mutex for this object
        self.__mutex = Lock()
        self.__current_map = current_map 
        self.__player_count = player_count
        self.__max_players=max_players
        self.__serverListAddress=serverListAddress
        self.__stopHeartBeat = Condition()
        self.__port = port
        #acquire the heartbeat mutex immediately, so that the heartBeat thread can never obtain it
        #until we release it in __stopHeartbeat()
        self.__stopHeartBeat.acquire()
        #register with the serverList
        self.__heartBeatThread = None
        self.refreshBy = serverBrowser.registerServer(self.__serverListAddress, port, name, 
                   description, self.__current_map, self.__player_count, self.__max_players, mods)

    def updatePlayercount(self, player_count):
        with self.__mutex:
            self.__player_count = player_count
        self.__doHeartBeat()

    def updateMaxPlayercount(self, max_players):
        with self.__mutex:
            self.__max_players = max_players
        self.__doHeartBeat()

    def updateMap(self, current_map):
        with self.__mutex:
            self.__current_map = current_map
        self.__doHeartBeat()

    def __startHeartbeat(self):
        #start the heartbeat thread
        self.__heartBeatThread = Thread(target=self.__heartBeatThreadTarget)
        self.__heartBeatThread.start()

    def stopHeartbeat(self):
        #if the heartbeat thread exists
        if self.__heartBeatThread is not None and self.__heartBeatThread.is_alive():
            self.__stopHeartBeat.release()
            self.__heartBeatThread.join()
        self.__stopHeartBeat.acquire()
        self.__heartBeatThread = None

    def __enter__(self):
        self.__startHeartbeat()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stopHeartbeat()
        #if exc_tb is not None:
        #    traceback.print_tb(exc_tb)
    
    def __doHeartBeat(self):
        with self.__mutex:
            print("Heartbeat")
            self.refreshBy = serverBrowser.heartbeat(self.__serverListAddress, self.__port, 
                                                           self.__current_map, self.__player_count, 
                                                           self.__max_players)

    def __heartBeatThreadTarget(self):
        print("Heartbeat thread started")
        while True:
            #this will wait for a shutdown signal until it's time for the next heartbeat
            #when that time elapses, then do a heartbeat and go back to waiting
            #this way, a shutdown signal can be sent at basically any time
            #and be handled immediately, the thread is always asleep otherwise,
            #and only ever wakes up when it actually has something to do.
            if not self.__stopHeartBeat.acquire(timeout=0.8*(self.refreshBy - time.time())):
                self.__doHeartBeat()
            else:
                print("Heartbeat thread ended")
                self.__stopHeartBeat.release()
                return
            
    def __del__(self):
        self.stopHeartbeat()