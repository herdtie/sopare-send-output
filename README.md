# sopare-send-output
Plugin for Sopare to send recognized sound patterns via unix domain socket to other python[3]-process

This contains 2 parts. First the sopare plugin itself that is called by sopare and sends sound patterns to a socket. Second a "listener" that receives the recognized sound patterns.

Sofar, this is pretty basic and more of a prove-of-concept that a useful program. Still, I find it worth preserving and sharing. Somebody (or me) might actually find this useful.

What is is already useful for is avoid the python3-conversion of sopare since the listener is already running in python3. So, just run your python3-plugin-code in the listener instead of sopare itself.

Also a noteworthy feature: this uses UDP, so if any of the 2 communications endpoints is killed the other end is not affected.
