import traceback
from serverRegister import Registration
import a2s
from time import sleep
import argparse
import socket
import curses
import curses.ascii
from collections import deque

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

last_command = ""
def main(screen):
    height, width = screen.getmaxyx()
    outputWindowBox, inputWindowBox, outputWindow, inputWindow = createWindows(screen)

    printing = lambda s: outputString(outputWindow, s)

    
    with Registration(args.remote, name=args.name, description=args.description, printLambda=printing) as re:
        command_list = deque(maxlen=100)
        while True:
            try:
                command = ""
                search_prefix = ""
                chars = []
                command_index = -1

                try:
                    while True:
                        char = screen.get_wch()
                        if isinstance(char, str):
                            if char == "\n" or char == "\r" or char == "\r\n":
                                command_list.appendleft(command)
                                command += "\n"
                                break
                            elif char == "\b":
                                command = command[:-1]
                            elif char == "\t":
                                command += "    "
                            else:
                                command += char
                            search_prefix = command
                        elif char == curses.KEY_RESIZE:
                            outputWindowBox, inputWindowBox, outputWindow, inputWindow = createWindows(screen)
                            height, width = screen.getmaxyx()
                            continue
                        elif char == curses.KEY_UP or char == curses.KEY_A2:
                            filtered_commands = list(filter(lambda x: x.startswith(search_prefix), command_list))
                            if len(filtered_commands) > (command_index + 1):
                                command_index += 1
                                command = filtered_commands[command_index]
                        elif char == curses.KEY_DOWN or char == curses.KEY_C2:
                            filtered_commands = list(filter(lambda x: x.startswith(search_prefix), command_list))
                            if command_index > 0 and len(filtered_commands) > 0:
                                command_index -= 1
                                command = filtered_commands[command_index]
                            else:
                                command_index = -1
                                command = ""
                        elif char == curses.ascii.ESC: #escape
                            command = ""
                        elif char == curses.KEY_BACKSPACE:
                            outputWindow.addstr("backspace\n")
                            command = command[:-1]
                        elif char == 127: #ctrl-backspace
                            outputWindow.addstr("ctr-backspace\n")
                            command = ""
                        
                        last_command = command

                        screen.move(height-2,len(command)+1)
                        inputWindow.erase()
                        inputWindow.addstr(command)
                        inputWindow.refresh()

                    inputWindow.erase()
                    screen.move(height-2,1)
                    inputWindow.refresh()
                    
                    outputWindow.addstr(command)
                    outputWindow.refresh()

                    if command.startswith("!"):
                        if command == "!history\n":
                            command_list.reverse()
                            for c in command_list:
                                outputWindow.addstr(c + "\n")
                                outputWindow.refresh()
                            command_list.reverse() # unreverse

                        continue

                    rcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    rcon.connect(("127.0.0.1", 9001))
                    rcon.sendall(bytes(command, "ASCII"))
                    rcon.close()
                except ConnectionRefusedError:
                    outputWindow.addstr("Failed to connect to RCON server. Is it running?\n")
                    outputWindow.refresh()
                except Exception as e:
                    outputWindow.addstr(traceback.format_exc())
                    outputWindow.refresh()   
            except Exception as e:
                outputWindow.addstr(traceback.format_exc())
                outputWindow.refresh()   
                raise e



try:
    curses.wrapper(main)
except Exception as e:
    print("Failed when running command: " + last_command)
    traceback.print_exc()
