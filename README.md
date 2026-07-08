# SecureTalk





## Overview

SecureTalk is an encrypted terminal chat application written in Python, based on a client-server model. Currently supported encryption algorithms:

\- **pgp**

\- **Caesar**

\- **XOR**



> ⚠️ **Currently only works on LAN networks.**

## Dependencies

This project requires **GnuPG (gpg)** to be installed on your local system system-wide, as the codebase relies on the underlying system binaries.

pip install prompt_toolkit python-gnupg

If you want to communicate from remote, you can use programs like Tailscale or hamachi to create a p2p Vpn

## Versions

The project has evolved through multiple versions, and is currently at v3.x, these are the main improvements for each version:



* **v1.0** - First version of the program, without encryption, with basic functions for sending and receiving text and images
* **v2.0** - Caesar encryption was added. Images don't have it though.
* **v2.2** - Adding of .txt files to store server and client setup data, in this way the start is much faster.
* **v3.0** - Xor encryption was added. Images still don't have it lol.
* **v3.1** - Servers can now advertise themselves in broadcast on the LAN, and can be discovered by clients.
* **v4.0** - Added pgp encryption, and now you have one single python file, as the project became a real p2p chat.



With each commit i'm trying to make the code better and to remove useless variables.



## Features:

* Encrypted messages (pgp, Caesar, XOR)
* p2p architecture
* Fast setup via saved configuration files
* gossip discovery method
* 100% terminal-based
* 100% Python



