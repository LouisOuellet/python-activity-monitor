#!/usr/bin/env python3
import os
import subprocess

def remove_service():
    # Stop the service
    os.system('sc stop "UserActivityMonitor"')

    # Delete the service
    os.system('sc delete "UserActivityMonitor"')

def remove_configuration():
    # Remove config files
    if os.path.exists('config/database.cfg'):
        os.remove('config/database.cfg')
    if os.path.exists('config/general.cfg'):
        os.remove('config/general.cfg')

if __name__ == "__main__":
    remove_service()
    remove_configuration()
