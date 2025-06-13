#!/usr/bin/env python3
"""
File Transfer Protocol Module

A reusable component that implements the file transfer protocol used by transmitter.py.
This module provides classes for sending and receiving files with checksum verification.
"""

import os
import socket
import hashlib
from pathlib import Path


def calculate_checksum(data):
    """Calculate MD5 checksum for data integrity verification."""
    return hashlib.md5(data).hexdigest()


class FileTransferProtocol:
    """Base class with common functionality for file transfer operations."""
    
    # Default chunk size for file transfers
    DEFAULT_CHUNK_SIZE = 4096
    
    def __init__(self, chunk_size=None):
        """Initialize with optional custom chunk size."""
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        # Callbacks for progress reporting and status updates
        self.on_progress = None
        self.on_status = None
    
    def set_callbacks(self, progress_callback=None, status_callback=None):
        """Set callbacks for progress and status updates."""
        self.on_progress = progress_callback
        self.on_status = status_callback
        
    def update_progress(self, percentage, message=None):
        """Report progress to callback if set."""
        if self.on_progress:
            self.on_progress(percentage, message)
        
    def update_status(self, message):
        """Report status message to callback if set."""
        if self.on_status:
            self.on_status(message)


class FileSender(FileTransferProtocol):
    """Handles sending files over a network socket with checksum verification."""
    
    def send_file(self, filepath, receiver_ip, port):
        """
        Send a file to a receiver at the specified IP address and port.
        Divides the file into chunks and transmits them with checksums for verification.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Check if file exists
            file_path = Path(filepath)
            if not file_path.is_file():
                self.update_status(f"Error: File '{filepath}' not found")
                return False

            # Get file information
            file_size = file_path.stat().st_size
            file_name = file_path.name

            self.update_status(f"Sending file: {file_name} ({file_size} bytes)")
            self.update_status(f"Connecting to {receiver_ip}:{port}...")
            
            # Create a socket and connect to the receiver
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((receiver_ip, port))
                except ConnectionRefusedError:
                    self.update_status(f"Error: Connection refused. Make sure the receiver is running at {receiver_ip}:{port}")
                    return False
                except socket.gaierror:
                    self.update_status(f"Error: Invalid address or hostname: {receiver_ip}")
                    return False
                
                # Send file metadata (name and size)
                header = f"{file_name}|{file_size}".encode('utf-8')
                header_size = len(header)
                s.sendall(f"{header_size:10d}".encode('utf-8'))  # Fixed-length header size
                s.sendall(header)
                
                # Send the file content in chunks
                total_chunks = (file_size + self.chunk_size - 1) // self.chunk_size  # Ceiling division
                chunks_sent = 0
                bytes_sent = 0
                
                with open(filepath, 'rb') as f:
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        
                        # Calculate checksum for the chunk
                        checksum = calculate_checksum(chunk)
                        
                        # Send the checksum and chunk size
                        chunk_header = f"{len(chunk)}|{checksum}".encode('utf-8')
                        s.sendall(f"{len(chunk_header):10d}".encode('utf-8'))
                        s.sendall(chunk_header)
                        
                        # Send the chunk data
                        s.sendall(chunk)
                        
                        chunks_sent += 1
                        bytes_sent += len(chunk)
                        
                        # Update progress
                        if file_size > 0:
                            progress = (bytes_sent / file_size) * 100
                            self.update_progress(
                                progress,
                                f"{chunks_sent}/{total_chunks} chunks ({bytes_sent}/{file_size} bytes - {progress:.1f}%)"
                            )
                
                # Send end-of-file marker
                s.sendall(b"0000000000")
                
                self.update_status("File sent successfully!")
                return True
                
        except KeyboardInterrupt:
            self.update_status("Transfer aborted by user.")
            return False
        except Exception as e:
            self.update_status(f"Error sending file: {str(e)}")
            return False


class FileReceiver(FileTransferProtocol):
    """Handles receiving files over a network socket with checksum verification."""
    
    def __init__(self, chunk_size=None, save_directory=None):
        """
        Initialize the file receiver.
        
        Args:
            chunk_size: Size of chunks to receive
            save_directory: Directory to save received files (defaults to current directory)
        """
        super().__init__(chunk_size)
        self.save_directory = Path(save_directory) if save_directory else Path.cwd()
        self.is_listening = False
    
    def stop_listening(self):
        """Stop the listening loop."""
        self.is_listening = False
    
    def receive_file_once(self, conn, addr):
        """
        Receive a single file from an established connection.
        
        Args:
            conn: Socket connection object
            addr: Address tuple (ip, port)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Receive header size first (10 bytes)
            header_size_bytes = conn.recv(10)
            if not header_size_bytes:
                self.update_status("Error: Connection closed before receiving header")
                return False
                
            header_size = int(header_size_bytes.decode('utf-8').strip())
            
            # Receive the header with file metadata
            header = conn.recv(header_size).decode('utf-8')
            if '|' not in header:
                self.update_status("Invalid file header received.")
                return False
                
            file_name, file_size = header.split('|')
            file_size = int(file_size)
            
            self.update_status(f"Receiving file: {file_name} ({file_size} bytes)")
            
            # Create the destination file path
            file_path = self.save_directory / file_name
            
            # Check if file already exists and add number suffix if needed
            counter = 1
            original_name = file_path.stem
            extension = file_path.suffix
            while file_path.exists():
                file_path = self.save_directory / f"{original_name}_{counter}{extension}"
                counter += 1
            
            # Receive file data in chunks
            bytes_received = 0
            chunks_received = 0
            error_chunks = 0
            
            with open(file_path, 'wb') as f:
                while True:
                    # Receive chunk header size
                    chunk_header_size_bytes = conn.recv(10)
                    
                    if not chunk_header_size_bytes or chunk_header_size_bytes == b"0000000000":
                        # End of file marker
                        break
                    
                    chunk_header_size = int(chunk_header_size_bytes.decode('utf-8').strip())
                    
                    # Receive chunk header (size|checksum)
                    chunk_header = conn.recv(chunk_header_size).decode('utf-8')
                    chunk_size, expected_checksum = chunk_header.split('|')
                    chunk_size = int(chunk_size)
                    
                    # Receive chunk data
                    chunk = b""
                    remaining = chunk_size
                    while remaining > 0:
                        data = conn.recv(min(4096, remaining))
                        if not data:
                            break
                        chunk += data
                        remaining -= len(data)
                    
                    # Verify checksum
                    actual_checksum = calculate_checksum(chunk)
                    if actual_checksum != expected_checksum:
                        self.update_status(f"Warning: Checksum mismatch on chunk {chunks_received + 1}. Data may be corrupted.")
                        error_chunks += 1
                    
                    # Write chunk to file
                    f.write(chunk)
                    
                    bytes_received += len(chunk)
                    chunks_received += 1
                    
                    # Update progress
                    if file_size > 0:
                        progress = (bytes_received / file_size) * 100
                        self.update_progress(
                            progress,
                            f"{chunks_received} chunks ({bytes_received}/{file_size} bytes - {progress:.1f}%)"
                        )
            
            # Report completion status
            if error_chunks > 0:
                self.update_status(f"File received with {error_chunks} corrupted chunks. Data integrity might be compromised.")
            else:
                self.update_status("File received successfully with verified integrity.")
            self.update_status(f"Saved as: {file_path}")
            return True
            
        except Exception as e:
            self.update_status(f"Error during file transfer: {str(e)}")
            return False
    
    def listen(self, host, port):
        """
        Listen for incoming connections and receive files continuously.
        
        Args:
            host: IP address to bind to
            port: Port number to listen on
            
        Returns:
            bool: True if gracefully exited, False on error
        """
        try:
            # Create a socket and bind to the specified address and port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Set socket option to reuse address to avoid "address already in use" errors
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Set a timeout so we can periodically check for exit flag
                s.settimeout(1.0)
                
                try:
                    s.bind((host, port))
                except socket.gaierror:
                    self.update_status(f"Error: Invalid address: {host}")
                    return False
                except OSError as e:
                    if e.errno == 98:  # Address already in use
                        self.update_status(f"Error: Port {port} is already in use")
                    else:
                        self.update_status(f"Error binding to {host}:{port}: {e}")
                    return False
                
                s.listen(1)
                self.update_status(f"Listening on {host}:{port} for incoming file transfers...")
                
                self.is_listening = True
                while self.is_listening:
                    try:
                        try:
                            conn, addr = s.accept()
                        except socket.timeout:
                            # Just a timeout to check if we should continue listening
                            continue
                        
                        self.update_status(f"Connected by {addr[0]}:{addr[1]}")
                        
                        with conn:
                            self.receive_file_once(conn, addr)
                            self.update_status("Waiting for next file transfer...")
                            
                    except KeyboardInterrupt:
                        self.update_status("Stopping receiver...")
                        self.is_listening = False
                        break
                    except Exception as e:
                        self.update_status(f"Error during file transfer: {str(e)}")
                        # Continue listening after an error with one transfer
                        continue
                
                return True
                    
        except KeyboardInterrupt:
            self.update_status("Receiver stopped by user.")
            return False
        except Exception as e:
            self.update_status(f"Critical error in receiver: {str(e)}")
            return False
