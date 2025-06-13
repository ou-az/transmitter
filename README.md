# Python Network File Transfer System

A robust file transfer system implemented in Python that allows for sending and receiving files over network sockets. This project includes both a Command-Line Interface (CLI) and a Graphical User Interface (GUI) for file transfers, with built-in integrity verification using MD5 checksums.

## Project Overview

This project implements a network file transfer protocol with the following features:
- File chunking for efficient transfer of large files
- MD5 checksum verification for data integrity
- Continuous listening mode for receivers
- Both CLI and GUI interfaces
- Modular design with reusable components

## Code Structure

The project is organized into the following key components:

### 1. `file_transfer_protocol.py`

Core module that implements the file transfer protocol:
- `FileTransferProtocol`: Base class with common functionality
- `FileSender`: Handles sending files with checksum verification
- `FileReceiver`: Manages receiving files with integrity checks

### 2. `transmitter.py`

Command-line interface (CLI) application that utilizes the protocol module:
- `send_file()`: Function to send files using the `FileSender` class
- `receive_file()`: Function to receive files using the `FileReceiver` class
- Command-line argument parsing for ease of use

### 3. `file_transfer_gui.py`

Graphical user interface (GUI) application built with Tkinter:
- File browser for selecting files to send
- IP address and port configuration
- Chunk size customization
- Progress bar and status updates
- Transfer log for monitoring activity

## How It Works

### File Transfer Protocol

The file transfer protocol operates as follows:

1. **Metadata Exchange**:
   - Sender transmits a header containing file name and size
   - Header size is sent first as a fixed-length 10-byte string

2. **Chunked File Transfer**:
   - File is divided into configurable chunks (default 4KB)
   - For each chunk, a header with chunk size and MD5 checksum is sent
   - Chunk header size is sent as a fixed-length 10-byte string
   - Chunk data follows the header

3. **End-of-File Marker**:
   - A special marker (`0000000000`) indicates the end of the file

4. **Verification**:
   - Receiver calculates MD5 checksum for each chunk
   - Compares with the checksum sent by the sender
   - Reports any integrity issues

5. **File Saving**:
   - Receiver handles filename conflicts by appending numeric suffixes
   - Writes chunks to disk as they are received

### Command-Line Interface

The CLI supports two modes:

1. **Send Mode**:
   ```
   python transmitter.py send <filepath> <receiver_ip> <port>
   ```

2. **Receive Mode**:
   ```
   python transmitter.py recv <ip> <port>
   ```

The receiver runs continuously, listening for new connections until manually stopped with Ctrl+C.

### Graphical User Interface

The GUI provides:
- File selection dialog
- IP address and port input fields
- Customizable chunk size
- Send button to initiate transfers
- Progress bar for visual feedback
- Status messages and transfer log

## Installation and Requirements

This project requires Python 3.6 or higher. No external dependencies are needed as it uses only the Python standard library.

## Usage Instructions

### CLI Usage

1. **Start the receiver**:
   ```
   python transmitter.py recv 127.0.0.1 5000
   ```

2. **Send a file**:
   ```
   python transmitter.py send path/to/file 127.0.0.1 5000
   ```

3. **Stop the receiver**:
   Press `Ctrl+C` in the receiver terminal window.

### GUI Usage

1. **Start the receiver** (CLI):
   ```
   python transmitter.py recv 127.0.0.1 5000
   ```

2. **Launch the GUI**:
   ```
   python file_transfer_gui.py
   ```

3. **Send a file**:
   - Click "Browse" to select a file
   - Enter receiver IP and port (default is 127.0.0.1:5000)
   - Optionally adjust chunk size
   - Click "Send File"

## Testing

To test the application:

1. **Start the receiver** in one terminal:
   ```
   python transmitter.py recv 127.0.0.1 5000
   ```

2. **Send a file** using either:
   - CLI: `python transmitter.py send test_file.txt 127.0.0.1 5000`
   - GUI: Launch `python file_transfer_gui.py` and use the interface

3. **Verify** that:
   - The receiver shows progress updates
   - The file is saved with the same name (or with numeric suffix if a conflict exists)
   - No checksum mismatch errors are reported

The receiver will continue to listen for additional file transfers until manually stopped.

## Future Improvements

Potential enhancements for the project:
- Compression support for more efficient transfers
- Retry mechanism for failed transfers
- Encryption for secure file transfers
- GUI for the receiver
- Transfer pause/resume functionality
- Batch file transfer support

## License

This project is developed for educational purposes and uses only the Python standard library as required.
