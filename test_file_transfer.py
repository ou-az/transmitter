#!/usr/bin/env python3
"""
Test file for file_transfer.py

This script contains unit tests and a simple integration test for the file transfer CLI application.
"""

import os
import time
import socket
import unittest
import tempfile
import threading
import subprocess
from pathlib import Path
from file_transfer import send_file, receive_file

class FileTransferTest(unittest.TestCase):
    """Test cases for file transfer functionality."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = Path(self.test_dir.name)
        
        # Create a test file with some content
        self.test_file_path = self.test_dir_path / "test_file.txt"
        with open(self.test_file_path, 'wb') as f:
            f.write(b"This is a test file content for transfer testing.\n" * 100)
        
        # Set up the port for testing
        self.test_port = 5555
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory and its contents
        self.test_dir.cleanup()
    
    def test_end_to_end_transfer(self):
        """Test file transfer in a controlled environment using threads."""
        # Create a directory to save the received file
        receive_dir = self.test_dir_path / "received"
        receive_dir.mkdir()
        
        # Use an event to synchronize the sender and receiver
        receiver_ready = threading.Event()
        transfer_complete = threading.Event()
        
        # Create a receiver thread
        def receiver_thread():
            # Set up the receiver socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', self.test_port))
                s.listen(1)
                
                # Signal that the receiver is ready
                receiver_ready.set()
                
                # Accept the connection and receive the file
                conn, addr = s.accept()
                with conn:
                    # Receive header size first (10 bytes)
                    header_size_bytes = conn.recv(10)
                    header_size = int(header_size_bytes.decode('utf-8').strip())
                    
                    # Receive the header with file metadata
                    header = conn.recv(header_size).decode('utf-8')
                    file_name, file_size = header.split('|')
                    file_size = int(file_size)
                    
                    # Create the destination file path
                    file_path = receive_dir / file_name
                    
                    # Receive and write the file
                    with open(file_path, 'wb') as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            data = conn.recv(min(4096, file_size - bytes_received))
                            if not data:
                                break
                            f.write(data)
                            bytes_received += len(data)
                    
                    # Signal that the transfer is complete
                    transfer_complete.set()
        
        # Start the receiver thread
        receiver = threading.Thread(target=receiver_thread)
        receiver.daemon = True
        receiver.start()
        
        # Wait for the receiver to be ready
        receiver_ready.wait(timeout=5)
        
        # Send the test file
        send_file(str(self.test_file_path), '127.0.0.1', self.test_port)
        
        # Wait for the transfer to complete
        transfer_complete.wait(timeout=5)
        
        # Verify that the file was received correctly
        received_file_path = receive_dir / self.test_file_path.name
        self.assertTrue(received_file_path.exists(), "Received file does not exist")
        
        # Compare the contents of the original and received files
        with open(self.test_file_path, 'rb') as original:
            original_content = original.read()
        with open(received_file_path, 'rb') as received:
            received_content = received.read()
        
        self.assertEqual(original_content, received_content, "File contents do not match")
    
    def test_command_line_local_transfer(self):
        """Test the command-line interface with actual subprocesses."""
        # Create a directory to save the received file
        receive_dir = self.test_dir_path / "cmd_received"
        receive_dir.mkdir()
        
        # Start the receiver process
        receiver_cmd = ["python", "file_transfer.py", "receive", str(receive_dir), str(self.test_port + 1)]
        receiver_process = subprocess.Popen(
            receiver_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the receiver time to start
        time.sleep(2)
        
        # Start the sender process
        sender_cmd = ["python", "file_transfer.py", "send", str(self.test_file_path), "127.0.0.1", str(self.test_port + 1)]
        sender_process = subprocess.Popen(
            sender_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the sender to complete
        sender_stdout, sender_stderr = sender_process.communicate(timeout=10)
        
        # Wait for the receiver to complete (it should terminate after receiving one file)
        try:
            receiver_stdout, receiver_stderr = receiver_process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            receiver_process.terminate()
            receiver_process.wait()
            receiver_stdout, receiver_stderr = receiver_process.communicate()
        
        # Verify that the file was received
        received_file_path = receive_dir / self.test_file_path.name
        self.assertTrue(received_file_path.exists(), "Received file does not exist")
        
        # Compare the contents of the original and received files
        with open(self.test_file_path, 'rb') as original:
            original_content = original.read()
        with open(received_file_path, 'rb') as received:
            received_content = received.read()
        
        self.assertEqual(original_content, received_content, "File contents do not match")


if __name__ == "__main__":
    unittest.main()
