See documentation [here](https://chiv2-community.github.io/C2ServerAPI/)

Build documentation locally by running `doxygen` in the top-level directory (where the Doxyfile is)

# Setting up an unchained server

Excessive moddification of ini files or other mods before starting this may cause issues. If you have problems, try completely deleting `%localappdata%/Chivalry 2` and reinstalling chivalry 2 before doing this tutorial again.

## Definitions:
* Host machine: 
  * The computer hosting the chivalry 2 server
* Host instance: 
  * The instance of chivalry 2 acting as the "server." A single machine may run chivalry 2 twice, with one instance running as a client and the other as a server.
* Client instance:
  * See above, but it's a client instead.
* Backend:
  * An instance of our [C2ServerBrowserBackend](https://github.com/Chiv2-Community/C2ServerBrowserBackend). We run one at `servers.polehammer.net`, so you don't have to. This imitates portions of the playfab API to send custom MOTD and server list results to clients that target it.

## initial setup

1. Install unchained on the host as you normally would. Make sure unchained is replacing the normal chivalry 2 launcher. (you will be prompted to do this on install)
2. Go to the 'server' tab of the unchained launcher and enter your server's name and other configuration

If Chivalry 2 has not run on this machine before, or you deleted `%localappdata%/Chivalry 2`:
Click "Launch headless" in the bottom right. Let this run for ~20 seconds to ensure that ini files are generated before closing all windows that opened. You may be prompted to download several files: Click "Yes"

**IMPORTANT FOR NFO HOSTS:** If you are using NFO hosting, there is a port conflict with UDP/7777. Change your game port to 7778 in the server tab. No other action is needed. If you do not do this then you will experience extreme gameplay degredation.

## Necessary ini Tweaks
There are two ini settings that must be set in order to successfully host. Navigate to `%localappdata%/Chivalry 2/Saved/Config/WindowsNoEditor` in your file browser and open `Game.ini`. Add the following lines to the top of the file:  
```ini
[/Script/TBL.TBLGameInstance]
FirstLoadCompleted=True

[/Script/TBL.TBLTitleScreen]
bSavedHasAgreedToTOS=True
```

**NOTE:** If the TBLGameInstance or TBLTitleScreen sections are already present somewhere in the file, add the lines to those sections instead of making a duplicate.

## launching
Go back to the server tab in the unchained launcher and click "Launch Headless". You may be prompted to download several files: Click "Yes". Two windows will open. The first is the unchained debug window, which you will see during normal unchaiend launches. The second is your server's RCON control panel. This registers your server with the unchained backend (so that it appears in the unchaiend in-game server list) and allows you to execute server commands. These commands are from the same list as the in-game console.

## port forwarding
NFO Hosts: NFO servers have automatic port forwarding--you don't have to do anything here.

Before anyone other than you can join your server, you need to forward your ports. (expose them to to the open internet)
You must forward the following ports:
- Game Port (default UDP/7777)
- Ping Port (default UDP/3075)

Additional ports that are used but do not need to be or should not be forwarded:
- RCON port (default TCP/9001)
- A2S port (default UDP/7071)

***The RCON port (TCP/9001) should not be exposed to the open internet!*** Doing this would give anyone and their grandma full freedom to execute admin commands on your server! They (likely) can't hack your machine through this, but they *can* ban people, kick people, and change the map to whatever they want! If you want your admins accessing this, use [ssh tunneling](https://www.ssh.com/academy/ssh/tunneling-example) or set up your firewall rules to allow only them!

The ports you need to forward are visible (and can be changed to whatever you want before launching) in the server tab of the unchained launcher. Doing this follows the same procedure as forwarding ports for any other game, and thus will not be described here. Tutorials for port forwarding can be found online.

# troubleshooting

## A2S Timed Out
On the initial start of your server, these messages are normal. The console attempts to connect to the chivalry server before it has actually had time to start up and listen. If these messages do not stop appearing after ~30 seconds, then there is something wrong.

1. Try sending a console command. 
   1. If you get an error in the server console, this means that the chivalry process is not listening on RCON. This indicates a plugin loading issue. Close the server windows and re-start it. If the issue persists, contact the Unchained Team for help.
   2. If you see the same console command appear in the debug output window, this indicates that the plugins are loaded, but the server has not yet loaded into the map to listen on the A2S port.
      1. Check if there is a "Substituted console command" line in the debug output. If there is one, contact the Unchained Team--this indicates there is an issue in the Unchained-Mods and map loading machinery.
      2. If there is no "Substituted console command" line, this suggests an ini misconfiguration. Go to the *Necessary ini Tweaks* section and ensure the required ini lines are present. If you keep having trouble, contact the Unchained Team

## Severe network lag
NFO hosts: Make sure your game port is NOT 7777. Change it to 7778.  

Other hosts: Make sure you don't have any applications using UDP/7777 on your computer.

## Known Issues
1. For the host instance, animations are bugged. There is no workaround for this other than launching another instance, joining as a client, and playing on that instead.
2. netcode is very sensitive to host and client FPS. It is strongly recommended that you cap the fps of the host instance, and advertise that fps in your server description. Clients should lock their fps to match. If the host is running at, for example, 120fps:
   * clients running at lower (<120) fps will get delayed hits, swing-throughs, and other netcode issues.
   * clients running at higher (>120) fps will get accelerated/early hits.
