#!/usr/bin/env python3
import time
import mysql.connector
import json
import threading
import ctypes
import os
import logging
from datetime import datetime

# Load MySQL settings from .cfg file
with open('config/database.cfg', 'r') as f:
    db_config = json.load(f)

# Load General settings from .cfg file
with open('config/general.cfg', 'r') as f:
    general_config = json.load(f)

# Create a directory for logs
if not os.path.exists('logs'):
    os.makedirs('logs')

# Setup logging
logging.basicConfig(filename=f'logs/{datetime.now().strftime("%Y%m%d")}.log',
                    level=general_config['log_level'],
                    format='%(asctime)s %(levelname)s %(message)s')

# Connect to the database
try:
    mydb = mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"]
    )
    logging.info("Database connection successful.")
except mysql.connector.Error as err:
    logging.error("Failed to connect to database: {}".format(err))
    exit(1)

mycursor = mydb.cursor()

# Check if tables exists, if not create them
try:
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            username VARCHAR(255) PRIMARY KEY,
            track BOOLEAN NOT NULL DEFAULT FALSE,
            idle_timeout INT,
            offline_timeout INT,
            status ENUM('online', 'idle', 'offline')
        )
    """)
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS Activity (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            active TIMESTAMP,
            FOREIGN KEY (username) REFERENCES Users(username)
        )
    """)
    logging.info("Tables checked/created successfully.")
except mysql.connector.Error as err:
    logging.error("Error while creating/checking tables: {}".format(err))

# Function to get current logged in username
def get_username():
    WTS_CURRENT_SESSION = -1
    WTS_UserName = 5
    WTSQuerySessionInformation = ctypes.windll.Wtsapi32.WTSQuerySessionInformationA
    WTSFreeMemory = ctypes.windll.Wtsapi32.WTSFreeMemory

    username = ctypes.create_string_buffer(257) 
    bytes = ctypes.pointer(ctypes.c_uint())
    
    if WTSQuerySessionInformation(None, WTS_CURRENT_SESSION, WTS_UserName, ctypes.byref(username), ctypes.byref(bytes)):
        user = username.value.decode('utf-8')
        WTSFreeMemory(username)
        return user
    else:
        return None

# Get the username
username = get_username()
logging.info("Current username: {}".format(username))

# Check if user exists, if not create it and set track to true
try:
    mycursor.execute("SELECT username FROM Users WHERE username = %s", (username,))
    result = mycursor.fetchone()
    if result is None:
        mycursor.execute(
            "INSERT INTO Users (username, track, idle_timeout, offline_timeout) VALUES (%s, TRUE, 300, 900)", (username,))
        mydb.commit()
        logging.info(f"User {username} successfully added to Users table with tracking enabled.")
except mysql.connector.Error as err:
    logging.error("Error occurred: {err}")

# Variable to track last active time
last_active = 0

# Function to get the idle time
def get_idle_time():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ('cbSize', ctypes.c_uint),
            ('dwTime', ctypes.c_uint),
        ]

    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)

    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
        millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
        return millis / 1000.0
    else:
        # could not get idle time, returning 0
        return 0

def update_db():
    # Check if user is being tracked
    mycursor.execute("SELECT track, idle_timeout, offline_timeout FROM Users WHERE username = %s", (username,))
    result = mycursor.fetchone()
    track, idle_timeout, offline_timeout = result
    if track:
        inactive_time = get_idle_time()
        if inactive_time < idle_timeout:
            status = 'online'
        elif inactive_time < offline_timeout:
            status = 'idle'
        else:
            status = 'offline'
        mycursor.execute("UPDATE Users SET status = %s WHERE username = %s", (status, username))
        if status == 'online':
            mycursor.execute("INSERT INTO Activity (username, active) VALUES (%s, NOW())", (username,))
        mydb.commit()
        logging.info(f"User {username} is {status}")
    # Call this function again in 60 seconds
    threading.Timer(60, update_db).start()

# Update the user activity initially
update_db()
