import base64
from Server.User import User
from Server.KeyManager import KeyManager
from Lobby import Lobby
import threading
import sqlite3
import socket
import pickle

class Server:
    def __init__(self, host="127.0.0.1", port=65432, max_clients=20):
        self.host = host  # Localhost
        self.port = port  # Arbitrary non-privileged port
        self.max_clients = max_clients
        self.Database = 'DataBase.db'
        self.manager = KeyManager()
        self.running = True
        self.active_users = []
        self.lobbies = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)  # Allow up to 5 pending connections
        print(f"Server listening on {host}:{port}...")

    def run(self):

        while self.running:
            while self.running:
                conn, address = self.server_socket.accept()

                if len(self.active_users) >= self.max_clients:
                    conn.sendall(b"Server is full. Try again later.\n")
                    conn.close()
                    print(f"Rejected connection from {address} — server full.")
                    continue

                # Accept new connection
                user = User(address, conn,)
                self.active_users.append(user)

                thread = threading.Thread(target=self.handle_client, args=(user, self.manager))
                thread.start()
                print(f"Active players: {len(self.active_users)} | Threads: {threading.active_count()}")

    # handles client requests
    def handle_client(self, user: User, manager: KeyManager):
        try:
            print(f"New connection from {user.data['username']} \n")
            if self.initial_key_exchange(user, manager):
                while True:
                    request = user.get_request()
                    if request is not None:
                        status = ''
                        msg = ''

                        if request['request'] == 'login':
                            msg, status = self.confirm_login(request['data']['username'], request['data']['password'])

                        if request['request'] == 'signup':
                            msg, status = self.create_user(request['data']['username'],  request['data']['password'])

                        if request['request'] == 'create_lobby':
                            msg, status = self.create_lobby(request['data'], user)

                        if request['request'] == 'get_lobby_list':
                            msg, status, data = self.get_lobby_list()

                        if request['request'] == 'join_lobby':
                            msg, status = self.join_lobby(request['data']['lobby_id'], user)

                        if request['request'] == 'game':
                            self.game_broadcast(request['data'], user)

                        user.send_response(status, msg)
                    else:
                        break

        except Exception as e:
            print(e)

        finally:
            # When client disconnects, remove them from active list
            if user in self.active_users:
                self.active_users.remove(user)
                print(f"User {user.data['username']} disconnected. Active players: {len(self.active_users)}")

            user.connection.close()

    def initial_key_exchange(self, user: User, manager: KeyManager):
        try:
            while True:
                request = user.get_request()
                if request['request'] == 'get public key':
                    status = 'key sent'
                    data = {'public_key': manager.get_public_key()}
                    user.send_response(status, 'public key sent', data)

                if request['request'] == 'return encrypted key':
                    encrypted_key = base64.b64decode(request['data']['encrypted_key'].encode('utf-8'))
                    decrypted_key = manager.decypher_aes_key(encrypted_key)
                    user.send_response('key received', 'encrypted key received')
                    user.data['aes_key'] = decrypted_key
                    print('Keys exchanged')
                    return True
        except Exception as e:
            print(e)
            return False

    # game related methods:
    def game_broadcast(self, user: User, data):
        lobby_id = data['lobby_id']
        for lobby in self.lobbies:
            if lobby.id == lobby_id:
                for player in lobby.playerList:
                    if player == user:
                        pass
                    else:
                        player.send_response(data)

    # return a list of all available lobbies
    def get_lobby_list(self):
        try:
            lobby_list = []
            for lobby in self.lobbies:
                if not lobby.full:
                    lobby_list.append((lobby.id, lobby.host.data['username'], len(lobby.playerList), lobby.max))

            return '', 'list sent', {'lobby_list': lobby_list}
        except Exception as e:
            print(e)
            return 'something went wrong', 'error', {'lobby_list': []}

    def join_lobby(self, lobby_id, user: User):
        for lobby in self.lobbies:
            if lobby.id == lobby_id:
                if lobby.add_player():
                    return f'joined {lobby.host.data["username"]}\'s lobby', 'success'
                return 'joining lobby failed', 'failed'
    # creates a new lobby
    def create_lobby(self, data, user: User):
        try:
            lobby_id = 1
            for lobby in self.lobbies:
                if lobby.id == lobby_id:
                    lobby_id += 1
            settings = data.values()
            host = user
            max_players = settings[0]
            time_limit = settings[1]
            difficulty = settings[2]

            print(f'lobby setting: {settings}')
            lobby = Lobby(lobby_id, host, max_players, time_limit, difficulty)
            self.lobbies.append(lobby)
            return 'lobby created', 'success'
        except Exception as e:
            print(e)
            return 'lobby creation failed', 'failed'

    # Database related methods:

    # checks if user exist
    def exist(self, username):
        # Connect to the database
        connection = sqlite3.connect(self.Database)
        cursor = connection.cursor()

        # Define a search query
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
    def create_user(self, username, password):
        try:
            with sqlite3.connect(self.Database) as connection:

                if not self.exist(username):
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
    def confirm_login(self, username, password):
        try:
            with sqlite3.connect(self.Database) as connection:

                cursor = connection.cursor()
                check_user = '''
                SELECT * FROM users WHERE username = ? AND password = ?
                '''

                cursor.execute(check_user, (username, password,))
                result = cursor.fetchall()

            if result:
                for row in result:
                    print(row)

                return 'login succeeded', 'success'
            else:
                print('user does not exist')
                return 'user doesnt exist', 'error'
        except Exception as e:
            print(e)
            return 'login failed', 'server error'


