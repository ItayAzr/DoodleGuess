import os
import socket
import threading
import sqlite3
import hashlib
import json
import struct
import GameServer

# checks if username is taken
def exist(username):
    # Connect to the database
    connection = sqlite3.connect('DataBase.db')
    cursor = connection.cursor()


    #Define a search query
    search_query = '''
        SELECT * FROM users WHERE username = ?;
        '''

    # Execute the query with a specific parameter
    cursor.execute(search_query, (username,))

    # Fetch all matching rows
    results = cursor.fetchall()

    connection.close()
    # Print the search results
    if results:
        print("Search results:")
        for row in results:
            print(row)
        return True
    else:
        print("No results found.")
        return False

# signup
def create_user(username, password):
    try:
        with sqlite3.connect('DataBase.db') as connection:

            if not exist(username):
                cursor = connection.cursor()
                insert_query = '''
                INSERT INTO users (username, password, wins, created_at)
                VALUES (?, ?, 0, DATETIME('now'))
                '''
                cursor.execute(insert_query, (username, password))


                print('User created successfully')
                return 'User created', 'success'
            else:
                print('user already exists')
                return 'user already exist', 'failed'
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return 'signup failed', 'error'

# login
def confirm_login(username, password):
    try:
        with sqlite3.connect('DataBase.db') as connection:

            cursor = connection.cursor()
            check_user = '''
            SELECT * FROM users WHERE username = ? AND password = ?
            '''

            cursor.execute(check_user, (username,password,))
            result = cursor.fetchall()

        if result:
            for row in result:
                print(row)


            return 'login succeeded','success'
        else:
            print('user does not exist')
            return 'user doesnt exist', 'error'
    except Exception as e:
        print(e)
        return 'login failed', 'server error'


def verify(request):
    try:
        request = request
        total = request['verify']
        request.pop('verify')
        current = hashlib.sha256(json.dumps(request).encode()).hexdigest()
        return total == current
    except Exception as e:
        print(e)
        return False

def create_lobby(data):
    settings = data.values()
    print(f'lobby setting: {settings}')


def handle_client(conn, address):
    print(f"New connection from {address}")
    while True:
        try:
            # Step 1: Receive the message length (4 bytes)
            msg_length_data = conn.recv(4)
            if not msg_length_data:
                print("Connection closed before receiving length")
                return

            msg_length = struct.unpack("!I", msg_length_data)[0]  # Convert 4 bytes to integer
            print(f"Expecting {msg_length} bytes...")

            # Step 2: Receive the complete JSON message
            data = b""
            while len(data) < msg_length:
                chunk = conn.recv(msg_length - len(data))
                if not chunk:
                    break
                data += chunk


            request = json.loads(data.decode()) # Receive data
            print(request)

            if "verify" not in request:
                response = {
                    'status': 'invalid request',
                    'data':{
                        "msg": "Missing verify attribute."
                    }
                }
                response = json.dumps(response).encode()
                conn.send(struct.pack("!I", len(response)))
                conn.send(response)
            elif verify(request):
                response = {
                    'status': 'invalid request',
                    'data': {
                        'msg': 'request type does not exist'
                    }
                }

                if request['request'] == 'login':
                    msg, status  = confirm_login(request['data']['username'],request['data']['password'])
                    response = {
                        'status': status,
                        'data': {
                            'msg': msg,

                        }
                    }


                if request['request'] == 'signup':
                    msg, status = create_user(request['data']['username'],  request['data']['password'])
                    response = {
                        'status': status,
                        'data': {
                            'msg': msg
                        }
                    }

                if request['request'] == 'create_lobby':
                    msg, status = create_lobby(request['data'])
                    response = {
                        'status': status,
                        'data': {
                            'msg': msg
                        }
                    }
                    #game_thread
                    #game_thread = threading.Thread(target=, args=(conn, address))

                # Send the response length first
                response = json.dumps(response).encode()
                conn.send(struct.pack("!I", len(response)))
                conn.send(response)
            else:
                response = {
                    'status': 'incomplete request',
                    'data': {
                        'msg': 'request is missing information'
                    }
                }
                response = json.dumps(response).encode()
                conn.send(struct.pack("!I", len(response)))
                conn.send(response)

        except Exception as e:
            print(e)
            break



def server_program():
    host = "127.0.0.1"  # Localhost
    port = 65432        # Arbitrary non-privileged port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)  # Allow up to 5 pending connections
    print(f"Server listening on {host}:{port}...")

    while True:
        conn, address = server_socket.accept() # Accept new connectio
        thread = threading.Thread(target=handle_client, args=(conn, address))
        thread.start()  # Start the thread to handle the client
        print(f"Active threads: {threading.active_count()}")



if __name__ == "__main__":
    server_program()