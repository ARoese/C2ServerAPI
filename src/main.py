from serverRegister import Registration
import a2s
from time import sleep
import argparse
import socket
import curses
import curses.ascii

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL) #so that sigint will actually kill all threads

##NOTE: Chivalry should be running locally for this test script to work. Otherwise, you should remove
##the a2s calls which will fail without an actual chivalry server running

##NOTE: Also, there should be a server list server running locally on port 8080

#REMOTE = "http://127.0.0.1:8080"

args = argparse.ArgumentParser(description="Register a Chivalry 2 server with the server browser")
args.add_argument('-r', "--remote", required=False, type=str, default="https://servers.polehammer.net")
args.add_argument('-n', "--name", required=False, type=str, default="Chivalry 2 Private Server")
args.add_argument('-d', "--description", required=False, type=str, default="")
args.add_argument('-c', "--rcon", required=False, type=int, default=9001)
args = args.parse_args()

def createWindows(screen, outputWindowBox=None, inputWindowBox=None, outputWindow=None, inputWindow=None):
    if outputWindowBox is not None:
        del outputWindowBox
    if outputWindow is not None:
        del outputWindow
    if inputWindowBox is not None:
        del inputWindowBox
    if inputWindow is not None:
        del inputWindow
    height, width = screen.getmaxyx()
    screen.refresh()
    outputWindowBox = curses.newwin(height-3, width, 0,0)
    outputWindowBox.box()
    outputWindowBox.addstr(0,10," Output ")
    #outputWindowBox.addstr(1,1,"0")
    outputWindowBox.refresh()

    inputWindowBox = curses.newwin(3, width, height-3,0)
    inputWindowBox.box()
    inputWindowBox.box()
    inputWindowBox.addstr(0,10," Chivalry 2 RCON ")
    #inputWindowBox.addstr(1,1,"0")
    inputWindowBox.refresh()

    outputWindow = curses.newwin(height-3-2, width-2, 1,1)
    #outputWindow.addstr(0,0,"0")
    outputWindow.refresh()

    inputWindow = curses.newwin(1, width-2, height-2,1)
    #inputWindow.addstr(0,0,"0")
    inputWindow.refresh()

    outputWindow.scrollok(True)
    return (outputWindowBox, inputWindowBox, outputWindow, inputWindow)

def safeOrd(char):
    try:
        return ord(char)
    except:
        return -1

def outputString(outputWindow, s):
    outputWindow.addstr(s + "\n")
    outputWindow.refresh()

def main(screen):
    height, width = screen.getmaxyx()
    outputWindowBox, inputWindowBox, outputWindow, inputWindow = createWindows(screen)

    printing = lambda s: outputString(outputWindow, s)

    
    
    with Registration(args.remote, name=args.name, description=args.description, printLambda=printing) as re:
        lastCommand = ""
        while True:
            command = ""
            while True:
                char = screen.getkey()
                #outputWindow.addstr(str(ord(char)))
                #outputWindow.addstr(str(curses.ascii.ESC))
                #outputWindow.refresh()
                if char == "KEY_RESIZE":
                    outputWindowBox, inputWindowBox, outputWindow, inputWindow = createWindows(screen)
                    height, width = screen.getmaxyx()
                    continue
                elif safeOrd(char) == curses.ascii.ESC: #escape
                    command = ""
                elif char == '\b':
                    outputWindow.addstr("backspace\n")
                    command = command[:-1]
                elif safeOrd(char) == 127: #ctrl-backspace
                    outputWindow.addstr("ctr-backspace\n")
                    command = ""
                elif char =='\n':
                    #outputWindow.addstr(str(len(command)))
                    if len(command) == 0:
                        command = lastCommand
                    lastCommand = command
                    command += "\n"
                    break
                else:
                    command += char
                screen.move(height-2,len(command)+1)
                inputWindow.erase()
                inputWindow.addstr(command)
                inputWindow.refresh()
            
            inputWindow.erase()
            screen.move(height-2,1)
            inputWindow.refresh()
            
            outputWindow.addstr(command)
            try:
                rcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                rcon.connect(("127.0.0.1", 9001))
                rcon.sendall(bytes(command, "ASCII"))
                rcon.close()
            except Exception as e:
                outputWindow.addstr(f"Error sending command: {str(e)}\n")
            outputWindow.refresh()   



try:
    curses.wrapper(main)
except Exception as e:
        print(str(e))
