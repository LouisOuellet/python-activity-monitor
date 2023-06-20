# User Activity Monitor

This is a Python service that monitors user activity in Windows environments. It checks the logged in user's status and stores the status information in a MySQL database, as well as in logs. The service has been designed to work well in a multi-user environment, making it ideal for tracking user activity in session-based remote desktops.

## Features

- **Monitor user status:** The service checks if a user is online, idle, or offline based on their activity.
- **Database storage:** The user's status information is stored in a MySQL database for easy retrieval and analysis.
- **Logging:** Activity and errors are logged daily. The log level can be set in the configuration.
- **Multi-user environment:** The service works well in a multi-user environment and correctly identifies the logged in user.
- **Remote desktop compatible:** The service can also track activity in session-based remote desktops.
- **Easy installation:** An installation script asks for the database connection info and log level and sets up the service automatically.

## Documentation

### Prerequisites

- Python 3
- MySQL

### Installation

1. Clone this repository.
2. Run the `install.py` script. This will install the necessary Python packages, set up the configuration files, and install the service. The script will ask for your MySQL connection info and the log level for the logs.

    ```sh
    python install.py
    ```

### Configuration

The configuration files are located in the `config` directory.

- `database.cfg`: Contains the MySQL connection information.
- `general.cfg`: Contains the log level.

### Running

The service runs automatically in the background after installation. It checks the user's status every minute.

### Uninstallation

To uninstall the service and remove the configuration files, run the `uninstall.py` script:

```sh
python uninstall.py
```

### Logs

The logs are stored in the `logs` directory, with a new log file created each day. The name of the log file is the date.