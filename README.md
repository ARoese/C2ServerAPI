See documentation [here](https://chiv2-community.github.io/C2ServerAPI/)

Build documentation locally by running `doxygen` in the top-level directory (where the Doxyfile is)

# Hosting your own server

## Definitions:
* Host machine: 
  * The computer hosting the chivalry 2 server
* Host instance: 
  * The instance of chivalry 2 acting as the "server." A single machine may run chivalry 2 twice, with one instance running as a client and the other as a server.
* Client instance:
  * See above, but it's a client instead.
* Backend:
  * An instance of our [C2ServerBrowserBackend](https://github.com/Chiv2-Community/C2ServerBrowserBackend). We run one at `servers.polehammer.net`, so you don't have to. This imitates portions of the playfab API to send custom MOTD and server list results to clients that target it.

## Preparation
1. Forward and make firewall rules allowing incoming connections to these ports: (more on this later)
   * UDP/7777 (Server port)
     * real-time game data is sent over this port
   * UDP/7071 (A2S query port)
     * game state data like map name and player count is advertised on this port
   * UDP/3075 (UDP Ping port)
     * This is used by the in-game server browser to check the ping to a server. This is ***NOT*** and ICMP ping. If it isn't open, it will list as 9999ms ping and disallow join attempts.

2. Clone this [C2ServerAPI](https://github.com/Chiv2-Community/C2ServerAPI) repository onto your host machine (yes, I did just link the repo you're reading off right now)
3. install [python3](https://www.python.org/downloads/) onto your host machine
4. use pip to install the dependencies 
   * ```pip install requests```

## Starting the Server

1. launch your server instance using our [C2GUILauncher](https://github.com/Chiv2-Community/C2GUILauncher) in modded mode. Ensure that you have the `C2ServerPlugin` mod selected to load. In future versions, this may not be the default.
2. In your server instance, open the console(`), type `open <map_name>?listen` into the console, where `<map_name>` is the name of the map you want to initially start in. A list of map names is maintained [here](https://docs.google.com/spreadsheets/d/1AJoXqLyCtDhWxnhQH3TuVGe-w8syoVtM/edit#gid=2059699818).
3. On your host machine, run the `testReg.py` script to register this server with the backend. While this script continues to run, your server will be "online" in the in-game server browser of modded clients.

>Clarification: You registered with `servers.polehammer.net` by default, and all clients use that by default. If you choose to register with a different server list, or if a client is using a different server list, then they will not see your server. You only need to worry about this if you intentionally change away from the default server list.

**testReg example usage:**

```python3 testReg.py --name "My server" --description "No RDMing pls. Run by DrLong"```

run `python3 testReg.py` for more help on arguments

## Known Issues
1. For the host instance, animations are bugged. There is no workaround for this other than launching another instance, joining as a client, and playing on that instead.
2. netcode is very sensitive to host and client FPS. It is strongly recommended that you cap the fps of the host instance, and advertise that fps in your server description. Clients should lock their fps to match. If the host is running at, for example, 120fps:
   * clients running at lower (<120) fps will get delayed hits, swing-throughs, and other netcode issues.
   * clients running at higher (>120) fps will get accelerated/early hits.

## Headless Servers

>This section is under construction. Some portions and tools required are not ready for public use.

Servers "with heads" run as if they were a client, rendering the game, gui, and everything as if they were a normal client. This can be very taxing on both the CPU and GPU, and highly inconvenient if you want to host and play on the same machine. (both instances will be eating resources) An instance can be launched "headless" so that it will not render the game and will only execute server-side logic. (or, at least, as little extra as possible) Doing this will bring that instance's resource demands to near-zero and thus help prevent server-side lag spikes.

To run a host instance headless, launch as usual but pass the `-nullrhi` flag in the command line arguments shown in the C2GUILauncher. No window will be launched, and no rendering will be done. You will hear audio from this instance. Unfortunately, this means you also cannot send inputs or console commands!

This issue is resolved with a combination of dll injection and blueprint mods. Set the initial map that the server will launch to `<INSERT MAP NAME HERE>` via the command line in the C2GUILauncher. Also, launch with the `TODO: SPECIAL RCON VERSION OF SERVERPLUGIN` mod enabled.

> TODO: make a blueprint map to spawn the zombie BP
> 
> TODO: get the serverplugin RCON set up fully for public distribution and use

The ServerRCONPlugin will launch a console window from the headless instance which will allow you to view the console. It will also listen on port TCP/9001 for commands you want the headless instance to execute. The `<INSERT MAP NAME HERE>` creates a persistent blueprint that will generate a steady stream of console commands for the RCON plugin to subsitute for it's own (your) commands sent to it on TCP/9001. 

***TCP/9001 should not be exposed to the open internet!*** Doing this would give anyone and their grandma full freedom to execute admin commands on your server! They can't hack your machine, but they *can* ban people, kick people, and change the map to whatever they want! If you want your admins accessing this, use [ssh tunneling](https://www.ssh.com/academy/ssh/tunneling-example) or set up your firewall rules to allow only them!

>TODO: add authentication to the RCON plugin as a base, and make a client program for it.
