## Transmitter Project

### Description

Develop a simple sender/receiver program using python or C++ to transmit files over a network using tcp socket streams.
The sender program will read a file, divide it into smaller chunks, and transmit the chunks to the receiver
over a socket connection. The receiver program will receive the chunks, reassemble them, and write the data back into a new file.

The project will demonstrate how to handle command line argument parsing, network communication, packet fragmentation, and error detection, focusing on using sockets to manage the lower-level transmission of data. 

- Bonus points:
    - Multi-threaded sender and receiver
    - Meaningfull error handling


### Usage
  `transmitter.py send <filename> <ip> <port>`
  `transmitter.py recv <ip> <port>`
### Notes
- Must use Git/Github for version control
- Cannot use external libraries, only Python standard library
- Must handle command line arguments