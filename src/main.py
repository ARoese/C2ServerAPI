import traceback
from serverRegister import Registration
import a2s
from time import sleep
import argparse
import socket
import curses
import curses.ascii
from collections import deque
import socket

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
args.add_argument('-g', "--game-port", required=False, type=int, default=7777)
args.add_argument('-p', "--ping-port", required=False, type=int, default=3075)
args.add_argument('-a', "--a2s-port", required=False, type=int, default=7071)
args.add_argument('-z', '--no-register', action='store_true', default=False, help="Don't register the server with the server browser")
args.add_argument('-x', '--password-protected', action='store_true', default=False, help="Indicate to the server that this server is password protected")
args.add_argument('-m', '--mod', nargs='*', action='append', help="A list of mods to communicate what is enabled to the server browser")
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
    try: 
        _, _, outputWindow, inputWindow = createWindows(screen)
        if args.no_register:
            outputWindow.addstr("Setting up rcon interface with no server browser listing.\n")
            outputWindow.refresh()
            process_rcon_interface(screen, outputWindow, inputWindow)
        else:
            outputWindow.addstr("Setting up rcon interface with server browser listing.\n")
            outputWindow.refresh()
            process_rcon_interface_with_registration(screen, outputWindow, inputWindow)
    except Exception:
        with open("RegisterUnchainedServer.errorlog.txt", "a") as f:
            traceback.print_exc(file=f)

def process_rcon_interface_with_registration(screen, outputWindow, inputWindow):
    printing = lambda s: outputString(outputWindow, s)
    parsed_mods = []
    
    for mod_string in args.mod: # No idea why argparse makes this a list of lists
        try:
            mod_string_actual = mod_string[0] # but it means we have to do this
            [org, name_and_version] = mod_string_actual.split('/')
            [name, version] = name_and_version.split('=')

            parsed_mods.append({
                "organization": org,
                "name": name,
                "version": version
            })
        except Exception as e:
            with open("RegisterUnchainedServer.errorlog.txt", "a") as f:
                print("Failed to parse mod string: " + mod_string_actual, file=f)
                traceback.print_exc(file=f)

    with Registration(args.remote, local_ip=get_local_ip(), name=args.name, description=args.description, printLambda=printing,
                      gamePort=args.game_port, pingPort=args.ping_port, queryPort=args.a2s_port, 
                      password_protected=args.password_protected, mods=parsed_mods):
        process_rcon_interface(screen, outputWindow, inputWindow)

def process_rcon_interface(screen, outputWindow, inputWindow):
    outputWindow.addstr("RCON Ready. Type commands in to the InputBox at the bottom of the screen, then press ENTER to execute the commands on the host server.\n")
    outputWindow.refresh()
    command_list = deque(maxlen=100)
    height, width = screen.getmaxyx()
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
                        _, _, outputWindow, inputWindow = createWindows(screen)
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
                rcon.connect(("127.0.0.1", args.rcon))
                rcon.sendall(bytes(command, "ASCII"))
                rcon.close()
            except ConnectionRefusedError:
                outputWindow.addstr("Failed to connect to RCON server. Is it running?\n")
                outputWindow.refresh()
            except Exception as e:
                with open("RegisterUnchainedServer.errorlog.txt", "a") as f:
                    print("Failed when running command: " + last_command, file=f)
                    traceback.print_exc(file=f)
                outputWindow.addstr(traceback.format_exc())
                outputWindow.refresh()   
        except Exception as e:
            with open("RegisterUnchainedServer.errorlog.txt", "a") as f:
                print("Failed when running command: " + last_command, file=f)
                traceback.print_exc(file=f)
            outputWindow.addstr(traceback.format_exc())
            outputWindow.refresh()   

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# Used for debugging if the program crashes
last_command = ""

try:
    curses.wrapper(main)
except Exception:
    with open("RegisterUnchainedServer.errorlog.txt", "a") as f:
        print("Failed when running command: " + last_command, file=f)
        traceback.print_exc(file=f)
