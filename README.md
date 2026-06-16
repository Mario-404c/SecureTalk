# SecureTalk





## Overview

SecureTalk is an encrypted terminal chat application written in Python, based on a client-server model. Currently supported encryption algorithms:

\- **Caesar**

\- **XOR**



> ⚠️ **Currently only works on LAN networks.**


## Dependencies
pip install prompt_toolkit
If you want to communicate from remote, you can use programs like Tailscale or hamachi to create a p2p Vpn

## Versions

The project has evolved through multiple versions, and is currently at v3.x, these are the main improvements for each version:



* **v1.0** - First version of the program, without encryption, with basic functions for sending and receiving text and images
* **v2.0** - Caesar encryption was added. Images don't have it though.
* **v2.2** - Adding of .txt files to store server and client setup data, in this way the start is much faster.
* **v3.0** - Xor encryption was added. Images still don't have it lol.
* **v3.1** - Servers can now advertise themselves in broadcast on the LAN, and can be discovered by clients.



With each commit i'm trying to make the code better and to remove useless variables.



## Features:

* Encrypted messages (Caesar, XOR)
* Client-server architecture
* Fast setup via saved configuration files
* Broadcast advertising.
* 100% terminal-based
* 100% Python

