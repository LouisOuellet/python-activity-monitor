#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from getpass import getpass

# List of packages to install
packages = [
    "mysql-connector-python",
    "pynput",
    "pywin32"
]

def install_requirements():
    # Install the packages
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def create_configuration():
    # Get MySQL connection info
    if not os.path.exists('config/database.cfg'):
        host = input("Enter MySQL host: ")
        user = input("Enter MySQL user: ")
        password = getpass("Enter MySQL password: ")
        database = input("Enter MySQL database: ")

        # Write config file
        with open('config/database.cfg', 'w') as f:
            json.dump({"host": host, "user": user, "password": password, "database": database}, f)

    # Get log level
    if not os.path.exists('config/general.cfg'):
        log_level = input("Enter log level (DEBUG, INFO, WARNING, ERROR, CRITICAL): ")

        # Write config file
        with open('config/general.cfg', 'w') as f:
            json.dump({"log_level": log_level}, f)

def install_service():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "monitor.py")

    # Use sys.executable to get the Python interpreter path, escape backslashes
    python_path = sys.executable.replace("\\", "\\\\")

    # Escape backslashes for the script path as well
    script_path = script_path.replace("\\", "\\\\")

    # Install the service
    os.system(f'sc create "UserActivityMonitor" binPath= "{python_path} {script_path}" start= auto DisplayName= "User Activity Monitor"')

if __name__ == "__main__":
    install_requirements()
    create_configuration()
    install_service()
