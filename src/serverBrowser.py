import requests
import json
from typing import AnyStr, Tuple
#from time import sleep

def __buildError(errorCode : int, errResponse: json) -> str:
    return ("Server could not be updated: error {}.\n"
            "Message: {}\n"
            "Context: {}\n"
            "Status: {}\n").format(errorCode, errResponse['message'], errResponse['context'], errResponse['status'])

def __checkResponse(response : requests.Response):
    try:
        parsed = response.json()
    except:
        raise RuntimeError("Server error (could not parse response body): " + str(response.status_code))
    
    if not 500 <= response.status_code < 600:
        raise RuntimeError(__buildError(response.status_code, parsed))
    else:
        raise RuntimeError("Server error: " + str(response.status_code))

def registerServer(address: AnyStr, port: int = 7777, name: AnyStr = "Chivalry 2 Server", 
                   description: AnyStr = "No description", current_map: AnyStr = "Unknown", 
                   player_count: int = -1, max_players: int = -1, mods = []) -> Tuple[str,float]:
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

    :returns: (str, str, float) The unique ID of the registered server,
        The key required to update this server registration in the future, and 
        The time by which the next heartbeat must be sent, or else this registration times out
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
    response = requests.post(address+"/api/v1/servers", json=serverObj)
    #print(response.text)
    if not response.ok:
        __checkResponse(response)
    else:
        jsResponse = response.json()
        return jsResponse['server']['unique_id'], jsResponse['key'], float(jsResponse['refresh_before'])
    
def updateServer(address : AnyStr, unique_id : str, key : str, port : int, 
                 player_count : int, max_players : int, current_map : str) -> None:
    """Send a heartbeat to the server browser backend
    
    Heatbeats must be sent periodically

    :param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.
    :param unique_id: The unique id for the server issued by the backend through the registerServer() function
    :param port: The port on which the chivalry server is listening on.
    :param player_count: The number of players currently in the server
    :param max_players: The max number of players that can be in this server at once
    :param current_map: The current map of the chivalry server. This can be updated later.

    :returns: The time by which the next heartbeat must be sent, or else this registration times out
    :raises: RuntimeError when a non-ok http status is received
    """
    updateBody = {
        "port": port,
        "player_count": player_count,
        "max_players": max_players,
        "current_map": current_map
    }
    updateHeaders = {
        "x-chiv2-server-browser-key": key
    }

    response = requests.put(address+"/api/v1/servers/"+unique_id, headers=updateHeaders, json=updateBody)
    print(response.text)
    if not response.ok:
        __checkResponse(response)
    else:
        return None
        
    
def heartbeat(address: AnyStr, unique_id : str, key : str, port : int):
    """Send a heartbeat to the server browser backend
    
    Heatbeats must be sent periodically

    :param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.
    :param port: The port on which the chivalry server is listening on.

    :returns: The time by which the next heartbeat must be sent, or else this registration times out
    :raises: RuntimeError when a non-ok http status is received
    """
    heartbeatObj = {
        "port": port
    }

    heartbeatHeaders = {
        "x-chiv2-server-browser-key": key
    }
    response = requests.post(address+"/api/v1/servers/" + unique_id + "/heartbeat", headers=heartbeatHeaders, json=heartbeatObj)
    #print(response.text)
    if not response.ok:
        __checkResponse(response)
    else:
        return float(response.json()['refresh_before'])
    
def getServerList(address: AnyStr):
    """Retreive a list of all Chivalry servers registered with the backend

    :param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.

    :returns: A string-representation of a JSON array of all listed servers

    :raises: RuntimeError when a non-ok http status is received
    """
    response = requests.get(address+"/api/v1/servers")
    if not response.ok:
        __checkResponse(response)
    else:
        return response.json()["servers"]

    
#print(registerServer("http://localhost:8080", 7777))
#sleep(5)
#print(heartbeat("http://localhost:8080", 7777))
#print(getServerList("http://localhost:8080"))