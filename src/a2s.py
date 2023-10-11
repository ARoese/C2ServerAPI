"""functions for communicating with an A2S port.

A2S is a valve protocol for requesting information about a game server such as the
current map, number of players, and max number of players. This port is usually
UDP/7071 for chivalry 2. Chivalry 2 only implements A2S_INFO and A2S_PING,
so only those are implemented here.

See the A2S_INFO class documentation to see what kind of useful information can be
returned here.

"""

import socket as __socket
import struct as __struct
import time as __time
from dataclasses import dataclass as __dataclass

#ping = bytes([0xFF,0xFF,0xFF,0xFF,0x69])

def __extractString(bts : bytes, offset : int) -> tuple[str,int]:
    """extract null-terminated string from bytes object

    @param bts: bytes object to extract string from
    @param offset: position of the first character in the string to exact

    @returns (string, offset of byte after null-terminator)
    """

    i = offset
    while bts[i] != 0 and i < len(bts):
        i+=1

    string = bts[offset:i].decode(encoding="utf-8")
    
    return string, i+1

@__dataclass
class A2S_INFO:
    """Data returned by A2S_INFO request"""
    protocolVersion: int = 0
    serverName: str = "Server name"
    mapName: str = "Unknown"
    folder: str = ""
    Game: str = "Chivalry 2"
    steamGameId: int = 0
    playerCount: int = 0
    maxPlayers: int = 0
    botCount: int = 0
    serverType: str = ""
    environment: str = ""
    isPrivate: bool = False
    vacEnabled: bool = False
    version: str = ""
    edf: int = 0

def getInfo(address : tuple[str, int] = ("127.0.0.1", 7071)) -> A2S_INFO:
    """Get server information

    @param address: address of the server to send the request to in the form ("127.0.0.1", 7071)/(address,port)
    @returns A2S_INFO object containing received data
    """
    #request __structure is defined by https://developer.valvesoftware.com/wiki/Server_queries
    request1 = bytes(
    [0xFF, 0xFF, 0xFF, 0xFF,
      0x54, 0x53, 0x6F, 0x75, 0x72, 0x63,
      0x65, 0x20, 0x45, 0x6E, 0x67, 0x69,
      0x6E, 0x65, 0x20, 0x51, 0x75, 0x65, 0x72, 0x79, 0x00])
    
    s = __socket.socket(type=__socket.SOCK_DGRAM)
    s.settimeout(5)
    s.sendto(request1, address)

    response,_ = s.recvfrom(1400)
    #print(response)
    #response __structure is defined by https://developer.valvesoftware.com/wiki/Server_queries
    #see A2S_INFO section
    _, protocolVersion = __struct.unpack_from("!xxxxcb", response, offset=0)
    serverName, ptr = __extractString(response,6)
    mapName, ptr = __extractString(response,ptr)
    folder, ptr = __extractString(response,ptr)
    Game, ptr = __extractString(response,ptr)
    (steamGameId, playerCount, maxPlayers, 
    botCount, serverType, environment, visibility,vac) = __struct.unpack_from("!hBBBccbb", response, offset=ptr)
    ptr += 9
    version, ptr = __extractString(response, ptr)
    edf, = __struct.unpack_from("!B", response, offset=ptr)
    
    return A2S_INFO(protocolVersion, serverName, 
        mapName, folder, Game, steamGameId, 
        playerCount, maxPlayers, botCount, 
        serverType, environment, visibility == 1, vac == 1, version, edf)

def ping(address : tuple[str, int]) -> float:
    """Ping the server and return how long it takes for it to respond, in seconds.

    This function is NOT an ICMP ping. This is a UDP ping via the A2S protocol, which is a more
    reliable way of determining the actual latency of the game server.
    
    @param address: address of the server to send the request to in the form ("127.0.0.1", 7071)/(address,port)
    @returns How long it took the server to respond to the ping in ms
    """
    pingrq = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0x69])

    s = __socket.__socket(type=__socket.SOCK_DGRAM)
    s.settimeout(5)
    start = __time.time()
    s.sendto(pingrq, address)
    response,_ = s.recvfrom(1400)
    stop = __time.time()
    return stop-start

#def getPlayers(address : tuple[str, int]):
#    #chivalry doesn't seem to implement this.
#    #passing the challenge results in the server simply not responding
#    #return None 
#    #request1 = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0x56, 0xFF, 0xFF, 0xFF, 0xFF])
#
#    s = __socket.__socket(type=__socket.SOCK_DGRAM)
#    s.sendto(request1, address)
#
#    response,_ = s.recvfrom(1400)
#    print(response)
#
#    challenge = __struct.unpack_from("!L", response, offset=5)[0]
#    print("Challenge was:", hex(challenge))
#    request2 = __struct.pack("!lcL",-1,bytes([0x41]),challenge)
#    print("request2:", request2)
#    s.sendto(request2, address)
#
#    response,_ = s.recvfrom(1400)
#    print(response)
