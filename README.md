# a2up - Automatic SFTP File Uploader

`a2up` (Auto to Upload) is a Python script that monitors a local directory and automatically uploads new files to a specified SFTP server directory.

## Features

- Watches a specified local directory for new files
- Automatically uploads new files to a remote SFTP directory
- Checks for existing files to avoid duplicates
- Creates remote directory if it doesn't exist
- Displays available space on remote directory
- Cleanly handles interruption (Ctrl+C)
- Command-line interface with helpful options

## Requirements

- Python 3.6+
- Required Python packages:
  - `watchdog` - for directory monitoring
  - `paramiko` - for SFTP connectivity

## Installation

1. Clone or download this repository
2. Install required dependencies:
```bash
pip install watchdog paramiko
Make the script executable (optional):
bash
chmod +x a2up.py
Usage
python a2up.py [OPTIONS]
Options
Option
Long Form
Description
-h
--help
Show help message and exit
-d
--destination
Remote directory to upload files to (required)
-f
--from
Local directory to watch for new files (required)
-s
--server
SFTP server address in user@ip.address format (required)
--space-available
Display available space on destination directory
Examples
Basic usage to monitor and upload:
bash
python a2up.py -f /local/path -d /remote/path -s user@192.168.1.100
Check available space:
bash
python a2up.py -f /local/path -d /remote/path -s user@192.168.1.100 --space-available
Show help:
bash
python a2up.py --help
How It Works
The script establishes an SFTP connection to the specified server
Creates the destination directory if it doesn't exist
Begins monitoring the local directory for new files
When a new file is detected:
Checks if it already exists on the remote server
If not, uploads it to the specified remote directory
Continues running until interrupted with Ctrl+C
Cleanly closes connections when stopped
Configuration
The script uses password authentication (prompts for password)
Default SFTP port is 22 (hardcoded)
Waits 1 second after file creation before uploading to ensure complete file write
Does not monitor subdirectories (non-recursive)
Notes
Requires network access to the SFTP server
User must have appropriate permissions on both local and remote directories
Only monitors for new file creation (not modifications or deletions)
Available space is displayed in MB when using --space-available
Use absolute paths for reliability
Troubleshooting
Connection failed: Check server address, network connectivity, and credentials
Permission denied: Verify user has write access to remote directory
Directory not found: Ensure local directory exists before running
Module not found: Install required dependencies with pip
Security Considerations
Password is entered at runtime (not stored)
Uses secure SFTP protocol
Recommend using SSH key authentication for production use (not currently implemented)
Future Improvements
Add SSH key authentication support
Add configuration file support
Implement recursive directory watching
Add file modification monitoring
Add retry mechanism for failed uploads
License
This project is released under the MIT License.
Contributing
Feel free to submit issues or pull requests to the repository.
Last updated: March 6, 2025

This README provides:
- Project overview and features
- Installation instructions
- Detailed usage examples
- Requirements and dependencies
- Explanation of how it works
- Configuration details
- Troubleshooting tips
- Security notes
- Potential improvements
- Licensing information
