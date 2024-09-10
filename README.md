A Python client library to interact with a Mooltipass device via Moolticuted WebSocket.

## Description

This project provides a Python library for interacting with Mooltipass devices through the Moolticuted daemon. It allows you to manage logins, get/set passwords, and more.

## Features

- Real-time communication with the Mooltipass device via moolticuted WebSocket.
- Convenience methods for common use cases, like getting passwords or setting credentials.
- CLI usage

## Library Usage

To use this library, simply import it into your Python project and start using its functions. For example:

```python

client = MoolticuteClient()

# Get a password for a specific service
response = client.get_password("example.com")
password = response.data.password

# Set a new credential for another service
response = client.set_password(
    "other.example.com",
    password="new_password",
    login="username",
    description="A description"
)
```

## CLI

The moolticutepy CLI provides a command-line interface to interact with your Mooltipass device. It allows you to list, get, and set passwords for various services.

### Commands

#### list_logins

Lists all logins stored on the Mooltipass device.

**Usage:** `list_logins`

**Example:**

```
$ moolticutepy list_logins
Entering management mode. Please approve prompt on device ...[OK]
- example.com []:
     * {'category': '0', 'date_created': '2024-07-30', 'date_last_used': '2024-07-30', 'description': 'description', 'favorite': -1, 'login': 'user@example.com'}
     * {'category': '0', 'date_created': '2024-07-30', 'date_last_used': '2024-07-30', 'description': 'description', 'favorite': -1, 'login': 'other.user@example.com'}
- other.example.com []:
     * {'category': '2', 'date_created': '', 'date_last_used': '2024-09-04', 'description': 'description', 'favorite': 20, 'login': 'username@example.com'}
```

#### get

Retrieves a password for a specific service.

**Usage:** `get <service> [-f|--fallback-service <fallback_service>] [-l|--login <login>]`

- `<service>`: the name of the service (required)
- `-f` or `--fallback-service`: an optional fallback service to use if the primary service is not available
- `-l` or `--login`: an optional login to use with the password

**Example:**

```
$ moolticutepy get private.example.com -f example.com
password123
```

#### set

Sets a password for a specific service.

**Usage:** `set <service> [-l|--login <login>] [-p|--password <password>] [-d|--description <description>]`

- `<service>`: the name of the service (required)
- `-l` or `--login`: an optional login to associate with the password
- `-p` or `--password`: the new password to set (optional, will prompt for input if not provided)
- `-d` or `--description`: an optional description to store with the password

**Example:**

```
$ moolticutepy set example.com -l admin -p newPassword123
Credentials stored for example.com [OK]
```

## License

This project is licensed under the [MIT License](https://github.com/rsrdesarrollo/moolticutepy/blob/master/LICENSE).

