# Transmitter - Simple File Transfer

A lightweight Python utility for sending and receiving files over a network using TCP sockets. This project implements a simple yet reliable file transfer protocol with a clean command-line interface.

## Features

- Simple command-line interface
- No external dependencies (Python standard library only)
- Basic progress reporting
- Graceful error handling
- Small and efficient (single file implementation)
- Cross-platform compatibility

## Requirements

- Python 3.6 or higher
- No additional packages required

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/transmitter.git
   cd transmitter
   ```

2. (Optional) Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Quick Start

### Sending a File

To send a file to a receiver:

```bash
python transmitter.py send <filename> <receiver_ip> <port>
```

Example:

```bash
python transmitter.py send example.txt 192.168.1.100 5000
```

### Receiving Files

To receive files, start the receiver:

```bash
python transmitter.py recv <ip> <port>
```

Example (listen on all interfaces):

```bash
python transmitter.py recv 0.0.0.0 5000
```

Press `Ctrl+C` to stop the receiver.

## How It Works

The file transfer process works as follows:

1. **Connection**: Sender establishes a TCP connection to the receiver
2. **Metadata**: Sender sends file metadata (name and size)
3. **Transfer**: File is sent in chunks (4KB by default)
4. **Completion**: Connection is closed after transfer

## Testing

### Basic Testing

1. Open two terminal windows

2. In the first terminal, start the receiver:

   ```bash
   python transmitter.py recv 127.0.0.1 5000
   ```

3. In the second terminal, send a file:

   ```bash
   python transmitter.py send example.txt 127.0.0.1 5000
   ```

### Testing Different File Sizes

Test with files of various sizes to ensure reliability:

```bash
# Create test files
dd if=/dev/zero of=small.bin bs=1M count=10    # 10MB
dd if=/dev/zero of=medium.bin bs=1M count=100  # 100MB
dd if=/dev/zero of=large.bin bs=1M count=1000  # 1GB

# Test transfer
python transmitter.py send small.bin 127.0.0.1 5000
python transmitter.py send medium.bin 127.0.0.1 5000
python transmitter.py send large.bin 127.0.0.1 5000
```

## Advanced Usage

### Using a Different Port

Specify a custom port number (must be above 1024 for non-root users):

```bash
# Receiver
python transmitter.py recv 0.0.0.0 8080

# Sender
python transmitter.py send file.txt 192.168.1.100 8080
```

### Network Testing

To test across different machines:

1. Find your local IP address:
   - Linux/macOS: `ifconfig | grep "inet "`
   - Windows: `ipconfig | findstr IPv4`

2. Start the receiver on the target machine:

   ```bash
   python transmitter.py recv <local_ip> 5000
   ```

3. Send a file from another machine:

   ```bash
   python transmitter.py send file.txt <target_ip> 5000
   ```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the receiver is running before sending
   - Check for firewall blocking the port
   - Verify IP address and port number

2. **File Not Found**
   - Check the file path is correct
   - Use absolute paths if needed

3. **Permission Denied**
   - Ensure you have read access to the file (sender)
   - Ensure you have write access to the destination directory (receiver)

## Implementation Details

### File Structure

- `transmitter.py`: Main CLI application
- `file_transfer_protocol.py`: Core transfer logic
- `file_transfer_gui.py`: Optional GUI interface (advanced)

### Transfer Protocol

1. **Connection**: TCP socket connection
2. **Metadata**: `<filename>|<filesize>`
3. **Data Transfer**: Raw file data in chunks
4. **Completion**: Connection close

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Note: For production use, consider adding encryption and authentication.*

## Basic Usage

## Sending a File

1. **Start the receiver**:

   ```bash
   python transmitter.py recv <ip> <port>
   ```

   Example:

   ```bash
   python transmitter.py recv 127.0.0.1 5000
   ```

2. **Send a file**:

   ```bash
   python transmitter.py send path/to/file 127.0.0.1 5000
   ```

3. **Stop the receiver**:

   Press `Ctrl+C` in the receiver terminal window.

### Using the GUI

1. **Start the receiver** (CLI):

   ```bash
   python transmitter.py recv 127.0.0.1 5000
   ```

2. **Launch the GUI**:

   ```bash
   python file_transfer_gui.py
   ```

3. **Send a file**:

   - Click "Browse" to select a file
   - Enter receiver IP and port (default is 127.0.0.1:5000)
   - Optionally adjust chunk size
   - Click "Send File"

## Testing the Application

1. **Start the receiver** in one terminal:

   ```bash
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
- **Compression support** for more efficient transfers
- **Retry mechanism** for failed transfers
- **Encryption** for secure file transfers
- **GUI for the receiver**
- **Transfer pause/resume** functionality
- **Batch file transfer** support

## License

This project is developed for educational purposes and uses only the Python standard library as required.
