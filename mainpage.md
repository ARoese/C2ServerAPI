\mainpage mainpage

\section Introduction
    Chivalry 2 currently has extremely limited access to it's behavior via programatic handles. For example, it is 
    only possible to enter commands or start games except for having a human present at the computer entering them. 
    This project aims to provide a convenient programatic interface to the Chivalry 2 game that allows users to access the
    in-game console and other gameplay elements using python.

    Currently, the major use of this is the implementation of unattended dedicated servers. This also provides enough
    flexibility to allow implementation of features such as end-game map voting on those dedicated servers. For more
    information on uses, see my other projects.

\section Project overview
    This project consists on two major components: inputLib and guiServer

\subsection inputLib
    InputLib is a simple back-end for sending keypresses to the chivalry window. It should not be used directly, but it
        is used heavily by guiServer

\subsection guiServer
    guiServer contains the Chivalry class, which serves to encapsulate the game. An instance of this chivalry class
    corresponds to a running instance of the chivalry 2 process. Member functions of the object act on that process to
    provide functionality such as opening the in-game console, sending commands to it, reading the output of those commands,
    and even getting the game-time remaining and detecting the game-state.

\section Examples
Below is an example demonstrating a simple use-case of the API and it's functions. It is mostly self-explanatory.

\code{.py}
from C2ServerAPI.guiServer import Chivalry
from time import sleep

game = Chivalry() #attach to the game window

game.openConsole()

if game.isMainMenu():
    game.consoleSend("open ffa_courtyard?listen")
else:
    game.consoleSend("servertravel ffa_courtyard")

sleep(30) #wait for the game to load

while not game.isGameEnd():
    game.closeConsole()
    #the y here at the start is required to open the chat box
    game.consoleSend("yThis is a test message to be sent in game chat by the server every 5 seconds!")
    game.openConsole()
    sleep(5)
\endcode
