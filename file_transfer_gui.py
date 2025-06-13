#!/usr/bin/env python3
"""
File Transfer GUI Application

A graphical interface for sending files using the file transfer protocol.
This GUI works with both the transmitter.py receiver and any application
using the FileReceiver class from file_transfer_protocol.py.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Import our reusable protocol component
from file_transfer_protocol import FileSender


class FileTransferGUI(tk.Tk):
    """Main application window for file transfer."""
    
    def __init__(self):
        super().__init__()
        
        # Configure the main window
        self.title("File Transmitter GUI")
        self.geometry("550x450")
        self.resizable(True, True)
        
        # Initialize variables
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to send files")
        self.progress_var = tk.DoubleVar()
        self.progress_var.set(0)
        self.file_path_var = tk.StringVar()
        self.receiver_ip_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="5000")
        self.chunk_size_var = tk.StringVar(value="4096")
        
        # Create the UI
        self.create_widgets()
        
        # Current transfer thread
        self.transfer_thread = None
        
    def create_widgets(self):
        """Create all UI elements."""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection section
        file_group = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_group, text="File to Send:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_group, textvariable=self.file_path_var, width=40).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(file_group, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        
        # Connection settings section
        conn_group = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        conn_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(conn_group, text="Receiver IP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(conn_group, textvariable=self.receiver_ip_var, width=15).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(conn_group, text="Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(conn_group, textvariable=self.port_var, width=15).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Transfer options section
        options_group = ttk.LabelFrame(main_frame, text="Transfer Options", padding="10")
        options_group.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(options_group, text="Chunk Size (bytes):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        chunk_size_entry = ttk.Entry(options_group, textvariable=self.chunk_size_var, width=10)
        chunk_size_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Send button
        self.send_btn = ttk.Button(main_frame, text="Send File", command=self.send_file)
        self.send_btn.pack(pady=10)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        # Progress bar
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(progress_frame, length=300, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status frame
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status bar
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Log console
        log_frame = ttk.LabelFrame(main_frame, text="Transfer Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
    
    def browse_file(self):
        """Open file browser dialog to select a file to send."""
        filename = filedialog.askopenfilename(
            title="Select File to Send",
            filetypes=[("All Files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.log(f"Selected file: {filename}")
    
    def log(self, message):
        """Add a message to the log console."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_progress(self, value, status_text=None):
        """Update progress bar and status text."""
        self.progress_var.set(value)
        self.progress_bar['value'] = value  # Update the progressbar directly
        if status_text:
            self.status_var.set(status_text)
            self.log(status_text)
    
    def send_file(self):
        """Handle the sending of a file."""
        # Get and validate input values
        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showerror("Error", "Please select a file to send.")
            return
        
        file_path = Path(filepath)
        if not file_path.exists():
            messagebox.showerror("Error", f"File not found: {filepath}")
            return
            
        try:
            receiver_ip = self.receiver_ip_var.get()
            port = int(self.port_var.get())
            chunk_size = int(self.chunk_size_var.get())
            if chunk_size <= 0:
                raise ValueError("Chunk size must be positive")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return
        
        # Disable send button during transfer
        self.send_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        # Start transfer in a separate thread
        self.transfer_thread = threading.Thread(
            target=self._send_file_thread,
            args=(filepath, receiver_ip, port, chunk_size),
            daemon=True
        )
        self.transfer_thread.start()
    
    def _send_file_thread(self, filepath, receiver_ip, port, chunk_size):
        """Thread function to handle file sending using FileSender from the protocol module."""
        try:
            # Initialize the file sender with the specified chunk size
            sender = FileSender(chunk_size=chunk_size)
            
            # Set up callbacks for progress and status updates
            def progress_callback(percentage, message):
                self.after(0, self.update_progress, percentage, message)
                
            def status_callback(message):
                self.after(0, self.log, message)
                
            sender.set_callbacks(progress_callback, status_callback)
            
            # Log initial status
            self.after(0, self.update_progress, 0, f"Connecting to {receiver_ip}:{port}...")
            
            # Send the file using our protocol implementation
            success = sender.send_file(filepath, receiver_ip, port)
            
            if success:
                self.after(0, self.update_progress, 100, "File sent successfully!")
                self.after(0, messagebox.showinfo, "Success", "File sent successfully!")
            else:
                # Error messages will be handled by the status callback
                pass
                
        except Exception as e:
            self.after(0, self.log, f"Error: {str(e)}")
            self.after(0, self.update_progress, 0, f"Error: {str(e)}")
            self.after(0, messagebox.showerror, "Transfer Error", str(e))
        
        finally:
            # Re-enable the send button
            self.after(0, self._reset_send_ui)
    
    def _reset_send_ui(self):
        """Reset the UI after file transfer."""
        self.send_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    app = FileTransferGUI()
    app.mainloop()
