import base64
import json
import time

from Server.User import User
from Server.KeyManager import KeyManager
from Lobby import Lobby
import threading
import sqlite3
import socket
import pickle

class Server:
    def __init__(self, host="127.0.0.1", port=65432, max_clients: int = 20):
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
            print(f"New connection from {user.get_data('username')} \n")
            if self.key_exchange(user, manager):
                while True:
                    request = user.get_request()
                    if request is not None:
                        status = ''
                        msg = ''
                        data = None

                        if request['request'] == 'login':
                            msg, status = self.confirm_login(request['data']['username'], request['data']['password'])
                            if status == 'success':
                                user.set_data('username', request['data']['username'])

                        if request['request'] == 'signup':
                            msg, status = self.create_user(request['data']['username'],  request['data']['password'])

                        if request['request'] == 'create_lobby':
                            msg, status, data= self.create_lobby(request['data'], user)

                        if request['request'] == 'get_lobby_list':
                            msg, status, data = self.get_lobby_list()

                        if request['request'] == 'join_lobby':
                            msg, status, data = self.join_lobby(request['data']['lobby_id'], user)

                        if request['request'] == 'start_game':
                            msg, status = self.start_game(request['data'], user)

                        if request['request'] == 'game':
                            self.game_broadcast(request['data'], user.lobby, user.get_data('username'))

                        user.send_response(status, msg, data)
                    else:
                        break

        except Exception as e:
            print(e)

        finally:
            if user.lobby is not None:
                self.check_empty_lobby(user.lobby.id)
            # When client disconnects, remove them from active list
            if user in self.active_users:
                self.active_users.remove(user)
                print(f"User {user.get_data('username')} disconnected. Active players: {len(self.active_users)}")

            user.connection.close()

    @staticmethod
    def key_exchange(user: User, manager: KeyManager):
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
                    user.set_data('aes_key', decrypted_key)
                    print('Keys exchanged')
                    return True
        except Exception as e:
            print(e)
            return False

    # game related methods:

    def start_game(self, data: dict, user: User):
        try:
            if user.lobby.host == user.get_data('username'):
                thread = threading.Thread(target=self.game_loop, args=(user.lobby,))
                thread.start()
                self.game_broadcast(data, user.lobby, user.get_data('username'))
                return 'game started', 'success'

            return 'user is not the host of the lobby', 'failed'

        except Exception as e:
            print(e)
            return 'failed to start game', 'failed'

    def game_loop(self, lobby: Lobby):
        for game_round in range(lobby.rounds):
            lobby.get_draw_word()
            guesser = {
                'skip': 'True',
                'word_length': len(lobby.word),
                'turn': 'no'
            }
            drawer = {
                'action': 'update',
                'word_length': lobby.word,
                'turn': 'yes'
            }
            # chooses the drawer and sends the word and word length
            for player in lobby.playerList:
                self.game_broadcast(guesser, lobby, player)
                for user in self.active_users:
                    username = user.get_data('username')
                    if username in lobby.playerList:
                        if username == player:
                            user.send_game_data(drawer)
                            self.game_broadcast(guesser, lobby, username)
                    thread = threading.Thread(target=self.handle_player, args=(user, username, lobby))
                    thread.start()

                start_time = time.time()
                while time.time() - start_time <= lobby.time_limit:
                    if self.check_empty_lobby(Lobby):
                        return 'lobby closed since it was empty'
                    time.sleep(0.1)

    def handle_player(self, user: User, username, lobby: Lobby):
        while lobby.in_round:
            try:
                request = user.get_request(game_request=True)
                if username == lobby.host:
                    self.game_broadcast({'data': request, 'turn': 'no', 'skip': 'True'}, lobby, username)
                elif 'guess' in request:
                    if username not in lobby.guessed:
                        if request['guess'] == lobby.word:
                            lobby.guessed.append(username)
                            data = {
                                'msg': 'guess is correct'
                            }
                        else:
                            data = {
                                'msg': 'incorrect guess'
                            }
                        user.send_game_data(data)


            except Exception as e:
                pass

    def check_empty_lobby(self, lobby_id, lobby=None):
        if lobby is not None:
            if len(lobby.playerList) == 0:
                self.lobbies.remove(lobby)
                print('deleted empty lobby')
                return True
        for LOBBY in self.lobbies:
            if LOBBY.id == lobby_id:
                if len(LOBBY.playerList) == 0:
                    self.lobbies.remove(Lobby)
                    print('deleted empty lobby')
                    return True
        return False

    def game_broadcast(self, data: dict, lobby: Lobby, sender: str):
        """
        :param data: the data that the server broadcasts to the players.
        :param lobby: the lobby of the player that sends the request
        :param sender: username of the player that sends the request
        :return: True if broadcast was completed successfully else, returns False
        """
        try:
            print(f'{type(data)}, data: {data}')
            skip_sender = bool(data.pop('skip'))
            for user in self.active_users:
                username = user.get_data('username')
                if username in lobby.playerList:
                    if skip_sender:
                        if username != sender:
                            user.send_game_data(data)
                    else:
                        user.send_game_data(data)

                    print(f'data sent to {username}')
            return True
        except Exception as e:
            print(e)
            return False

    # return a list of all available lobbies
    def get_lobby_list(self):
        try:
            lobby_list = []
            for lobby in self.lobbies:
                if not lobby.full:
                    lobby_list.append((lobby.id, lobby.host, len(lobby.playerList), lobby.max))

            return '', 'list sent', {'lobby_list': lobby_list}
        except Exception as e:
            print(e)
            return 'something went wrong', 'error', {'lobby_list': []}

    def join_lobby(self, lobby_id, user: User):
        for lobby in self.lobbies:
            if lobby.id == lobby_id:
                joined = lobby.add_player(user.get_data('username'))
                data = { }
                try:
                    if joined:
                        lobby_data = {'lobby': base64.b64encode(pickle.dumps(lobby)).decode()}
                        user.lobby = lobby
                        data = {'action': 'update', 'add_player': user.get_data('username'), 'skip': 'True'}
                        return f'joined {lobby.host}\'s lobby', 'success', lobby_data
                    return 'joining lobby failed', 'failed', data

                except Exception as e:
                    return 'joining lobby failed', 'failed', data

                finally:
                    if joined:
                        self.game_broadcast(data, lobby, user.get_data('username'), )

    # creates a new lobby
    def create_lobby(self, data: dict, user: User):
        try:
            lobby_id = 1
            for lobby in self.lobbies:
                if lobby.id == lobby_id:
                    lobby_id += 1
            settings = data.values()
            host = user.get_data('username')
            max_players = int(data['max_players'])
            time_limit = int(data['time_limit'])
            rounds = int(data['rounds'])
            difficulty = data['difficulty']

            print(f'lobby setting: {settings}')
            lobby = Lobby(lobby_id, host, max_players, time_limit, rounds, difficulty)
            self.lobbies.append(lobby)
            user.lobby = lobby
            return 'lobby created', 'success', {'lobby': base64.b64encode(pickle.dumps(lobby)).decode()}
        except Exception as e:
            print(e)
            return 'lobby creation failed', 'failed', None

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
            for user in self.active_users:
                if user.get_data('username') == username:
                    return 'user is already logged in', 'failed'
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


