#!/usr/bin/env python3
# File: a2up.py

import sys
import os
import time
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import paramiko
import signal

class FileWatcher(FileSystemEventHandler):
    def __init__(self, sftp_client, source_dir, dest_dir):
        self.sftp = sftp_client
        self.source_dir = source_dir
        self.dest_dir = dest_dir

    def on_created(self, event):
        if event.is_directory:
            return
        
        # Get the new file path
        source_path = event.src_path
        filename = os.path.basename(source_path)
        dest_path = os.path.join(self.dest_dir, filename)

        # Check if file already exists on server
        try:
            self.sftp.stat(dest_path)
            print(f"File {filename} already exists on server, skipping...")
            return
        except FileNotFoundError:
            # File doesn't exist, proceed with upload
            pass

        # Wait briefly to ensure file is fully written
        time.sleep(1)
        
        try:
            print(f"Uploading {filename} to {self.dest_dir}")
            self.sftp.put(source_path, dest_path)
            print(f"Successfully uploaded {filename}")
        except Exception as e:
            print(f"Error uploading {filename}: {str(e)}")

def get_available_space(sftp, directory):
    """Get available space in bytes for the remote directory"""
    try:
        statvfs = sftp.statvfs(directory)
        available_bytes = statvfs.f_bavail * statvfs.f_frsize
        return available_bytes
    except Exception as e:
        print(f"Error getting available space: {str(e)}")
        return None

def setup_sftp_connection(server):
    """Establish SFTP connection"""
    try:
        username, hostname = server.split('@')
        transport = paramiko.Transport((hostname, 22))
        transport.connect(username=username, password=input("Enter password: "))
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp, transport
    except Exception as e:
        print(f"Failed to connect to SFTP server: {str(e)}")
        sys.exit(1)

def signal_handler(sig, frame, sftp, transport):
    """Handle Ctrl+C to cleanly close connection"""
    print("\nDisconnecting from SFTP server...")
    if sftp:
        sftp.close()
    if transport:
        transport.close()
    sys.exit(0)

def print_help():
    """Print help menu"""
    help_text = """
SFTP File Uploader (a2up.py)
Usage: python a2up.py [OPTIONS]

Options:
  -h, --help            Show this help message and exit
  -d, --destination     Remote directory to upload files to
  -f, --from           Local directory to watch for new files
  -s, --server         SFTP server address (format: user@ip.address)
  --space-available    Display available space on destination directory
"""
    print(help_text)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-d', '--destination')
    parser.add_argument('-f', '--from')
    parser.add_argument('-s', '--server')
    parser.add_argument('--space-available', action='store_true')
    
    args = parser.parse_args()

    # Handle help flag
    if args.help or not any(vars(args).values()):
        print_help()
        sys.exit(0)

    # Validate required arguments
    if not all([args.destination, args.from, args.server]):
        print("Error: Missing required arguments (-d, -f, -s)")
        print_help()
        sys.exit(1)

    # Validate source directory exists
    if not os.path.isdir(args.__getattribute__("from")):
        print(f"Error: Source directory '{args.__getattribute__('from')}' does not exist")
        sys.exit(1)

    # Setup SFTP connection
    sftp, transport = setup_sftp_connection(args.server)

    # Handle space-available flag
    if args.space_available:
        space = get_available_space(sftp, args.destination)
        if space is not None:
            print(f"Available space in {args.destination}: {space / (1024*1024):.2f} MB")
        sftp.close()
        transport.close()
        sys.exit(0)

    # Setup signal handler for Ctrl+C
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, sftp, transport))

    # Ensure destination directory exists
    try:
        sftp.stat(args.destination)
    except FileNotFoundError:
        try:
            sftp.mkdir(args.destination)
            print(f"Created destination directory: {args.destination}")
        except Exception as e:
            print(f"Error creating destination directory: {str(e)}")
            sftp.close()
            transport.close()
            sys.exit(1)

    # Start watching directory
    event_handler = FileWatcher(sftp, args.__getattribute__("from"), args.destination)
    observer = Observer()
    observer.schedule(event_handler, args.__getattribute__("from"), recursive=False)
    observer.start()

    print(f"Watching {args.__getattribute__('from')} for new files...")
    print("Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
    sftp.close()
    transport.close()

if __name__ == "__main__":
    main()
