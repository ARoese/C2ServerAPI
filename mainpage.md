\mainpage mainpage

\section Introduction
    Chivalry 2 currently has extremely limited access to it's behavior via programatic handles. For example, it is 
    only possible to enter commands or start games except for having a human present at the computer entering them. 
    This project aims to provide a convenient programatic interface to the Chivalry 2 game that allows users to access the
    in-game console and other gameplay elements using python.

    Currently, the major use of this is the implementation of unattended dedicated servers. This also provides enough
    flexibility to allow implementation of features such as end-game map voting on those dedicated servers. For more
    information on uses, see my other projects. Facilities for registering hosted servers with a centralized server list
    are also included.

\section Project overview
    This project consists on two major components: server control, and server registration

\subsection serverControl Server control
    Controlling the Chivalry 2 process (the host) is done via the Chivalry class. An instance of this class represents an
        instance of the Chivalry 2 game on the local computer. Control of the running game can be done via method calls
        on the corresponding Chivalry class instance.

\code{.py}
from C2ServerAPI import Chivalry
#creates an instance of the chivalry class, which attaches to the Chivalry 2 process running on the local
#machine
game = Chivalry()

print(game.getTimeRemaining()) #prints how much time is left in the map stage
game.openConsole() #open the in-game console
game.consoleSend("exit") #send the "exit" command via the in-game console. This will close the game.
\endcode

\subsection serverRegistration Server registration
    Servers can be registered with a server list so that they can be found and joined easily by players. A
        server list serves as a central repository for information about what servers are currently live, how to
        join them, and what mods should be installed before joining those servers.

    Server registration is abstracted by the Registration class. Instances of this class represent a current
        registration with a remote [server list backend](https://github.com/Chiv2-Community/chivalry2-unofficial-server-browser). These registrations are kept valid via heartbeats on a separate thread
        so long as the object is alive. This class supports context manager syntax, seen below:

\code{.py}
from C2ServerAPI import Registration

with Registration("http://localhost:8080") as reg:
    #server loop
    #maybe you could do some map voting here
    #this block of code could run for hours on end
    #and the registration will be kept valid

print("Server closed")
#at this point, the registration is no longer being kept valid, and may time out at any moment
#later versions of this API may de-register the server after the "with" block is exited
\endcode

\section Examples
Below is an example demonstrating a simple use-case of the API and it's functions. It is mostly self-explanatory.

\code{.py}
from C2ServerAPI import Chivalry, Registration
from time import sleep

game = Chivalry() #attach to the game window

game.openConsole()

if game.isMainMenu():
    game.consoleSend("open ffa_courtyard?listen")
else:
    game.consoleSend("servertravel ffa_courtyard")

sleep(30) #wait for the game to load

with Registration("http://localhost:8080", current_map="ffa_courtyard") as reg:
    while not game.isGameEnd():
        game.closeConsole()
        #the y here at the start is required to open the chat box
        game.consoleSend("yThis is a test message to be sent in game chat by the server every 5 seconds!")
        game.openConsole()
        sleep(5)
\endcode
