# Transmitter Project Requirements

## Project Overview
Develop a simple sender/receiver program to transmit files over a network using TCP socket streams. The application will:
- Read a file and divide it into chunks
- Transmit chunks over a network socket
- Receive and reassemble chunks into a complete file
- Handle command-line arguments appropriately

## Technical Requirements

### Core Requirements
1. **File name and functionality**:
   - Rename `file_transfer.py` to `transmitter.py`
   - Focus on the core functionality of chunked file transfer

2. **Command Line Interface**:
   - Must support the exact syntax specified:
     - `transmitter.py send <filename> <ip> <port>`
     - `transmitter.py recv <ip> <port>`
   - Current implementation needs adjustment for the receiver command (no save directory parameter)

3. **Technology Constraints**:
   - Use Python's standard library only (our current implementation complies)
   - Must use Git/GitHub for version control

4. **Core Functionality**:
   - File reading and chunking (already implemented)
   - Network communication via sockets (already implemented)
   - Packet fragmentation (implemented with our chunking mechanism)
   - Error detection (need to enhance)

### Bonus Features
1. **Multi-threaded implementation**:
   - Consider implementing multi-threading for both sender and receiver
   - Our GUI implementation already uses threads; CLI version could be enhanced

2. **Meaningful error handling**:
   - Enhance error detection and recovery
   - Implement more robust error messaging
   - Add validation for network conditions and failures

## Required Changes to Current Implementation

1. **File and Command Structure Changes**:
   - Rename main file to `transmitter.py`
   - Update command parsing to match required syntax
   - For `recv` command, use current directory as default save location

2. **Simplification**:
   - Remove GUI implementation (not required by specifications)
   - Focus on enhancing the CLI implementation

3. **Enhancement Opportunities**:
   - Add multi-threading to core file transfer functionality
   - Improve error handling and reporting
   - Enhance packet fragmentation with checksums or verification

## Implementation Plan
1. Create new `transmitter.py` based on current `file_transfer.py`
2. Adjust command-line argument handling to match required syntax
3. Implement default save directory for receiver
4. Add multi-threading support for file operations
5. Enhance error handling and reporting
6. Add packet integrity verification

## Testing Requirements
- Test with files of various sizes
- Test with different network conditions
- Verify correct file reassembly
- Test error handling with simulated failures
