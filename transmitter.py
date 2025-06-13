#!/usr/bin/env python3
"""
Transmitter Project

A simple sender/receiver program to transmit files over a network using TCP socket streams.
The sender program reads a file, divides it into chunks, and transmits the chunks to the receiver.
The receiver program receives the chunks, reassembles them, and writes the data to a new file.

Usage:
    Send mode: transmitter.py send <filename> <ip> <port>
    Receive mode: transmitter.py recv <ip> <port>
"""

import os
import sys
import socket
import argparse
import threading
import hashlib
from pathlib import Path

# Import our reusable file transfer protocol classes
from file_transfer_protocol import FileSender, FileReceiver


def send_file(filepath, receiver_ip, port):
    """
    Send a file to a receiver at the specified IP address and port.
    Uses the reusable FileSender class from file_transfer_protocol module.
    """
    try:
        # Create a file sender instance
        sender = FileSender()
        
        # Configure status and progress callbacks to print to console
        def console_status(message):
            print(message)
            
        def console_progress(percentage, message):
            print(f"\r{message}", end="", flush=True)
        
        sender.set_callbacks(console_progress, console_status)
        
        # Send the file using the protocol implementation
        success = sender.send_file(filepath, receiver_ip, port)
        
        return success
            
    except KeyboardInterrupt:
        print("\nTransfer aborted by user.")
        return False
    except Exception as e:
        print(f"\nError sending file: {e}")
        return False


def receive_file(receiver_ip, port):
    """
    Listen for incoming connections and receive files.
    Uses the reusable FileReceiver class from file_transfer_protocol module.
    Continuously listens after each file transfer for new connections.
    Press Ctrl+C to stop listening and exit.
    """
    try:
        # Create a file receiver instance
        receiver = FileReceiver()
        
        # Configure status and progress callbacks to print to console
        def console_status(message):
            print(message)
            
        def console_progress(percentage, message):
            print(f"\r{message}", end="", flush=True)
        
        receiver.set_callbacks(console_progress, console_status)
        
        # Start listening for incoming file transfers
        success = receiver.listen(receiver_ip, port)
        return success
                    
    except KeyboardInterrupt:
        print("\nReceiver stopped by user.")
        return False
    except Exception as e:
        print(f"\nCritical error in receiver: {e}")
        return False


def main():
    """Parse command-line arguments and execute the appropriate mode."""
    if len(sys.argv) < 2:
        print("Error: Missing command")
        print("Usage:")
        print("  transmitter.py send <filename> <ip> <port>")
        print("  transmitter.py recv <ip> <port>")
        return
    
    command = sys.argv[1].lower()
    
    if command == "send":
        if len(sys.argv) < 5:
            print("Error: Missing arguments for send command")
            print("Usage: transmitter.py send <filename> <ip> <port>")
            return
        
        filename = sys.argv[2]
        ip = sys.argv[3]
        
        try:
            port = int(sys.argv[4])
        except ValueError:
            print(f"Error: Invalid port number: {sys.argv[4]}")
            return
        
        send_file(filename, ip, port)
        
    elif command == "recv":
        if len(sys.argv) < 4:
            print("Error: Missing arguments for recv command")
            print("Usage: transmitter.py recv <ip> <port>")
            return
            
        ip = sys.argv[2]
        
        try:
            port = int(sys.argv[3])
        except ValueError:
            print(f"Error: Invalid port number: {sys.argv[3]}")
            return
            
        receive_file(ip, port)
        
    else:
        print(f"Error: Unknown command: {command}")
        print("Usage:")
        print("  transmitter.py send <filename> <ip> <port>")
        print("  transmitter.py recv <ip> <port>")


if __name__ == "__main__":
    main()
