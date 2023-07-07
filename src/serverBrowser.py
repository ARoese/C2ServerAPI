import requests
import json
from typing import AnyStr
#from time import sleep

def registerServer(address: AnyStr, port: int = 7777, name: AnyStr = "Chivalry 2 Server", 
                   description: AnyStr = "No description", current_map: AnyStr = "Unknown", 
                   player_count: int = -1, max_players: int = -1, mods = []):
    """Register a chivalry server with a server browser backend.

    :param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.
    :param port: The port on which the chivalry server is listening on.
    :param name: The name for this server that will be listed in the browser
    :param description: A description of the server that will be listed in the browser
    :param current_map: The current map of the chivalry server. This can be updated later.
    :param player_count: The number of players currently in the server
    :param max_players: The max number of players that can be in this server at once
    :param mods: TODO: UNIMPLEMENTED A list of mods that this server is running, that clients
        should download and install before joining.

    :returns: The time by which the next heartbeat must be sent, or else this registration times out
    :raises: RuntimeError when a non-ok http status is received
    """
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
    """Send a heartbeat to the server browser backend
    
    Heatbeats must be sent periodically

    :param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.
    :param port: The port on which the chivalry server is listening on.
    :param current_map: The current map of the chivalry server. This can be updated later.
    :param player_count: The number of players currently in the server
    :param max_players: The max number of players that can be in this server at once

    :returns: The time by which the next heartbeat must be sent, or else this registration times out
    :raises: RuntimeError when a non-ok http status is received
    """
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
    """Retreive a list of all Chivalry servers registered with the backend

    :param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.

    :returns: A string-representation of a JSON array of all listed servers

    :raises: RuntimeError when a non-ok http status is received
    """
    response = requests.get(address+"/servers")
    if not response.ok:
        raise RuntimeError("Failed to retreive server list: error " + response.status_code)
    else:
        return response.json()["servers"]

    
#print(registerServer("http://localhost:8080", 7777))
#sleep(5)
#print(heartbeat("http://localhost:8080", 7777))
#print(getServerList("http://localhost:8080"))