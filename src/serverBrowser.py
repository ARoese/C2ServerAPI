import requests
import json
from typing import AnyStr, Tuple
#from time import sleep

class ResponseError(RuntimeError):
    def __init__(self, message: str, code: int, underlying: Exception = None):
        super().__init__(message)
        self.code = code
        self.underlying = underlying

def __buildError(errorCode : int, errResponse: json) -> str:
    return ("Server could not be updated: error {}.\n"
            "Message: {}\n"
            "Context: {}\n"
            "Status: {}\n").format(errorCode, errResponse.get('message'), errResponse.get('context'), errResponse.get('status'))

def __checkResponse(response : requests.Response) -> None:
    try:
        parsed = response.json()
    except:
        raise ResponseError("Server error (could not parse response body): " + str(response.status_code), response.status_code)
    
    if not 500 <= response.status_code < 600:
        raise ResponseError(__buildError(response.status_code, parsed), response.status_code)
    else:
        raise ResponseError("Server error: " + str(response.status_code), response.status_code)

def registerServer(address: AnyStr, local_ip: AnyStr, gamePort: int = 7777, pingPort: int = 3075, queryPort: int = 7071, name: AnyStr = "Chivalry 2 Server", 
                   description: AnyStr = "No description", current_map: AnyStr = "Unknown", 
                   player_count: int = -1, max_players: int = -1, mods = [], printLambda=print) -> Tuple[str,float]:
    """Register a chivalry server with a server browser backend.

    @param address: The URL of the serverlist to register with. This should be in the form 
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

    @returns (str, str, float) The unique ID of the registered server,
        The key required to update this server registration in the future, and 
        The time by which the next heartbeat must be sent, or else this registration times out
    @exception RuntimeError when a non-ok http status is received
    """
    serverObj = {
        "ports": {
            "game": gamePort,
            "ping": pingPort,
            "a2s": queryPort
        },
        "name": name,
        "description": description,
        "current_map": current_map,
        "player_count": player_count,
        "max_players": max_players,
        "local_ip_address": local_ip, 
        "mods": mods
    }
    response = requests.post(address+"/api/v1/servers", json=serverObj)
    if not response.ok:
        __checkResponse(response)
    else:
        jsResponse = response.json()
        return jsResponse['server']['unique_id'], jsResponse['key'], float(jsResponse['refresh_before'])
        
def updateServer(address : AnyStr, unique_id : str, key : str, 
                 player_count : int, max_players : int, current_map : str, printLambda=print) -> None:
    """Send a heartbeat to the server browser backend
    
    Heatbeats must be sent periodically

    @param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.
    @param unique_id: The unique id for the server issued by the backend through the registerServer() function
    @param player_count: The number of players currently in the server
    @param max_players: The max number of players that can be in this server at once
    @param current_map: The current map of the chivalry server. This can be updated later.

    @returns The time by which the next heartbeat must be sent, or else this registration times out
    @exception RuntimeError when a non-ok http status is received
    """
    updateBody = {
        "player_count": player_count,
        "max_players": max_players,
        "current_map": current_map
    }
    updateHeaders = {
        "x-chiv2-server-browser-key": key
    }

    response = requests.put(address+"/api/v1/servers/"+unique_id, headers=updateHeaders, json=updateBody)
    #print(response.text)
    if not response.ok:
        __checkResponse(response)
    else:
        return None
    
def delete(address: AnyStr, unique_id : str, key : str, printLambda=print) -> None:
    """Send a heartbeat to the server browser backend
    
    Heatbeats must be sent periodically

    @param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.
    @param unique_id: The unique id for the server issued by the backend 
        through the registerServer() function
    @param key: The access key required to update or modify servers. 
        Issued by the backend through the registerServer() function

    @returns true or false; if the server has been deleted on the backend
    @exception RuntimeError when a non-ok http status is received
    """
    
    updateHeaders = {
        "x-chiv2-server-browser-key": key
    }

    response = requests.delete(address+"/api/v1/servers/"+unique_id, headers=updateHeaders, json={})
    #print(response.text)
    if not response.ok:
        __checkResponse(response)
    else:
        return None
    
def heartbeat(address: AnyStr, unique_id : str, key : str, port : int, printLambda=print) -> float:
    """Send a heartbeat to the server browser backend
    
    Heatbeats must be sent periodically

    @param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.
    @param unique_id: The unique id for the server issued by the backend through the registerServer() function

    @returns The time by which the next heartbeat must be sent, or else this registration times out
    @exception RuntimeError when a non-ok http status is received
    """
    for i in range(0, 10):
        try:
            heartbeatHeaders = {
                "x-chiv2-server-browser-key": key
            }
            response = requests.post(address+"/api/v1/servers/" + unique_id + "/heartbeat", headers=heartbeatHeaders)
            #print(response.text)
            if not response.ok:
                __checkResponse(response)
            else:
                return float(response.json()['refresh_before'])
        except ResponseError as e:
            if e.code == 404:
                raise e
        except Exception as e:
            printLambda("Error sending heartbeat: " + str(e))
            printLambda("Retrying heartbeat")

            if i == 9:
                raise e
        
def getServerList(address: AnyStr, printLambda=print) -> str:
    """Retreive a list of all Chivalry servers registered with the backend

    @param address: The URL of the serverlist to register with. This should be in the form 
        `http://0.0.0.0:8080`.

    @returns A string-representation of a JSON array of all listed servers

    @exception RuntimeError when a non-ok http status is received
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