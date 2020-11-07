# sopare-send-output
Plugin for Sopare to send recognized sound patterns via unix domain socket to other python[3]-process

This contains 2 parts. First the sopare plugin itself that is called by sopare and sends sound patterns to a socket. Second a "listener" that receives the recognized sound patterns.

Sofar, this is pretty basic and more of a proof-of-concept than a useful program. Still, I find it worth preserving and sharing. Somebody (like future me) might actually find this useful.

What this is already useful for is to avoid the python3-conversion of sopare. Since the listener is already running in python3, you can just run your python3-plugin-code in the listener instead of a sopare plugin.

Also a noteworthy feature: this uses UDP, so if any of the 2 communications endpoints is killed the other end is not affected. You can just re-start each of the two (`sopare -l` and/or `sopare-listen.py`) and the other program will only print one warning and then continue working.

However, if you want to have this on Windows you need to replace the unix domain sockets with a different kind of socket.

# Installation
- install sopare, get it to run, teach it some sound patterns
- clone this repo
- create symlink inside your sopare/plugins directory:
  `cd /path/to/sopare/plugins ;`
  `ln -s /path/to/this/repo/sopare-plugins/send-output .`

When your run `sopare -l` now, you should see a message `Initializing socket at ...` at the end of the initial output, just before sopare outputs.

In another shell `cd` to the `sopare-send-output/listener` directory and run `./sopare-listen.py`. This should output that it binds to the socket and `Listening for data...`. When sopare recognizes sound patterns, you should see their description in both terminals now.

# Todo
- move constants and maybe even encode/decode functions to another module that both plugin and listener import
- do something with output in listener
