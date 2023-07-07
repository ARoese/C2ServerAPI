import requests
import json
from typing import AnyStr
#from time import sleep

def registerServer(address: AnyStr, port: int = 7777, name: AnyStr = "Chivalry 2 Server", 
                   description: AnyStr = "No description", current_map: AnyStr = "Unknown", 
                   player_count: int = -1, max_players: int = -1, mods = []):
    serverObj = {
        "port": port,
        "name": name,
        "description": description,
        "current_map": current_map,
        "player_count": player_count,
        "max_players": max_players,
        "mods": mods
    }
    response = requests.post(address+"/register", json=serverObj)
    if not response.ok:
        raise RuntimeError("Server could not be registered: error " + response.status_code)
    else:
        return float(response.json()['refresh_before'])
    
def heartbeat(address: AnyStr, port: int = 7777, 
              current_map: AnyStr = "Unknown", 
              player_count: int = -1, max_players: int = -1):
    heartbeatObj = {
        "port": port,
        "current_map": current_map,
        "player_count": player_count,
        "max_players": max_players
    }
    response = requests.post(address+"/heartbeat", json=heartbeatObj)
    if not response.ok:
        raise RuntimeError("Heartbeat failure: error " + response.status_code)
    else:
        return float(response.json()['refresh_before'])
    
def getServerList(address: AnyStr):
    response = requests.get(address+"/servers")
    if not response.ok:
        raise RuntimeError("Failed to retreive server list: error " + response.status_code)
    else:
        return response.json()["servers"]

    
#print(registerServer("http://localhost:8080", 7777))
#sleep(5)
#print(heartbeat("http://localhost:8080", 7777))
#print(getServerList("http://localhost:8080"))