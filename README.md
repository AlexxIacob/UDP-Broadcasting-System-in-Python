# UDP-Broadcasting-System-in-Python

A simple UDP broadcasting implementation in Python where multiple nodes communicate with each other simultaneously.

Each node sends N messages to all other nodes and listens for incoming messages. Every message is 1024 bytes: the first byte contains the sender index, the next 1003 bytes are random data, and the last 20 bytes are a SHA-1 checksum used to verify message integrity. Each received message is logged as OK or FAIL depending on whether the checksum matches.

## Requirements

- Python 3.x

## Usage

Configure nodes in a text file with the number of broadcasts on the first line followed by IP and port pairs:
```
1000
127.0.0.1 5000
127.0.0.1 5001
127.0.0.1 5002
```

Start a single node:
```
python bcastnode.py config.txt 0
```

Start multiple nodes at once:
```
startnodes.bat config.txt 0 4   # Windows
./startnodes.sh config.txt 0 4  # Linux
```

## How it works

Each node waits 30 seconds on startup to allow all other nodes to initialize before broadcasting begins. A node stops automatically after sending N messages and receiving N*M messages, where M is the total number of nodes.

## Output

Each node generates two log files:

- `node_X.log` - all received messages with OK or FAIL status and SHA-1 checksums
- `node_X_errors.log` - any errors encountered during execution
