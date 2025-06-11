import base64
import hashlib
import os
import pickle
import socket
import json
import struct

import select
from certifi.core import exit_cacert_ctx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from Lobby import Lobby


class Client:
    def __init__(self, host, port):
        self.Lobby = None
        self.username = 'Guest'
        self.logged_in = False
        self.AES_key = AESGCM.generate_key(128)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((host, port))  # Connect to server
        print(f"Connected to server at {host}:{port}")

    def get_public_key(self):
        while True:
            request = self.create_request('get public key')
            response = self.send_data(request, False)
            print(type(response['data']))
            if response['status'] == 'key sent':
                return response['data']['public_key']

    def key_exchange(self):
        try:
            rsa_public_key = serialization.load_pem_public_key(self.get_public_key().encode('utf-8'))
            # Encrypt AES key with RSA
            encrypted_key = rsa_public_key.encrypt(
                self.AES_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_key_base64 = base64.b64encode(encrypted_key).decode()
            data = {
                'encrypted_key': encrypted_key_base64
            }
            request = self.create_request('return encrypted key', data)
            self.send_data(request, False)
        except Exception as e:

            print(e)

    def decrypt_message(self, encrypted_data):
        """
        Decrypts a base64-encoded JSON message (nonce + ciphertext + tag).
        Returns a Python dictionary.
        """
        # Decode from base64 to raw bytes
        encrypted_data = base64.b64decode(encrypted_data)

        # Split the nonce and ciphertext
        nonce = encrypted_data[:12]
        ciphertext_and_tag = encrypted_data[12:]

        # Decrypt
        aesgcm = AESGCM(self.AES_key)
        json_data = aesgcm.decrypt(nonce, ciphertext_and_tag, associated_data=None)

        # Parse JSON back to dict
        return json.loads(json_data.decode("utf-8"))

    def encrypt_message(self, request: dict):
        """
        Encrypts a Python dictionary as JSON using AES-GCM.
        Returns a base64-encoded string of nonce + ciphertext + tag.
        """
        aesgcm = AESGCM(self.AES_key)
        nonce = os.urandom(12)  # GCM nonce must be 12 bytes

        # Convert dict to JSON string, then to bytes
        json_data = json.dumps(request).encode("utf-8")

        # Encrypt (ciphertext includes the 16-byte tag at the end)
        ciphertext = aesgcm.encrypt(nonce, json_data, associated_data=None)

        # Concatenate nonce + ciphertext and base64-encode it
        encrypted = base64.b64encode(nonce + ciphertext).decode("utf-8")
        return encrypted

    def recv_all(self, length):
        try:
            data = b''
            while len(data) < length:
                chunk = self.soc.recv(length - len(data))
                if not chunk:
                    return None  # connection closed
                data += chunk
            return data
        except Exception as e:
            print(e)

    def game_listen(self):
        print('listening for game data...')
        try:
            ready = False
            if self.Lobby.waiting:
                ready, _, _ = select.select([self.soc], [], [], 1)
            elif self.Lobby.GIM:
                ready, _, _ = select.select([self.soc], [], [], 1)
            if ready:
                print('ready to receive data')
                try:
                    print('waiting for response from the server...')
                    response_length_data = self.recv_all(4)

                    response_length = struct.unpack("!I", response_length_data)[0]
                    print(f"Expecting {response_length} bytes...")

                except Exception as e:
                    print(e)
                    return {'error': 'failed to receive msg length'}
                response_data = self.recv_all(response_length)
                if response_data:
                    print('received response from server')
                    return self.decrypt_message(response_data.decode('utf-8'))
                else:
                    return {'error': 'no data received'}
        except ConnectionResetError as e:
            print('connection to server closed')
            return {'error': 'disconnected from server'}
        except Exception as e:
            print(e)
            return {'error': e}

    def listen(self, encrypt: bool = True):

        print('listening...')
        try:
            print('waiting for response from the server...')
            response_length_data = self.recv_all(4)

            response_length = struct.unpack("!I", response_length_data)[0]
            print(f"Expecting {response_length} bytes...")

            # Receive full response data
            response_data = self.recv_all(response_length)
            if response_data:
                print('received response from server')
                if encrypt:
                    return self.decrypt_message(response_data.decode('utf-8'))
                return json.loads(response_data.decode('utf-8'))
            else:
                return {'error': 'no data received'}
        except ConnectionResetError as e:
            print('connection to server closed')
            return {'error': 'disconnected from server'}
        except Exception as e:
            print(e)
            return {'error': e}

    def send_data(self, request: dict, encrypt: bool = True, game: bool = False):
        """
        :param request: a dictionary that is sent to the server
        :param encrypt: a boolean variable, if true: initial rsa exchange was completed and server has AES key,
         sends a crypted request. if false: server does not have AES key, sends a non-crypted request.
         assumes server has AES key (type = True) unless told otherwise (type = False)
        :return: the response from the server, decrypts it if necessary.
        """
        print(f'request: {request}')
        if not encrypt:
            data = json.dumps(request).encode('utf-8')
        else:
            data = self.encrypt_message(request).encode('utf-8')
            print(f'encrypted request: {type(data)}, {data}')

            # Step 1: Send the message length first (4 bytes)
        self.soc.send(struct.pack("!I", len(data)))
        # Step 2: Send the actual JSON data
        self.soc.sendall(data)
        print('request sent')
        response = None
        if game:
            if self.Lobby.waiting:
                response = self.game_listen()
        else:
            response = self.listen(encrypt)
        print(f'response: {response}')
        if response is not None:
            try:
                if 'checksum' not in response or 'error' in response:
                    return None
                else:
                    checksum = response['checksum']
                    response.pop('checksum')
                    current_checksum = hashlib.sha256(json.dumps(response).encode('utf-8')).hexdigest()
                    if current_checksum == checksum:
                        return response
                    else:
                        return None
            except Exception as e:
                print(e)

    def set_lobby(self, lobby):
        print(pickle.loads(lobby))
        self.Lobby = pickle.loads(lobby)
        print(self.Lobby)

    @staticmethod
    def create_request(action: str, data: dict = None) -> dict:
        if data is None:
            data = {}
        request = {
            "request": action,
            'data': data
        }
        checksum = hashlib.sha256(json.dumps(request).encode('utf-8')).hexdigest()
        # add the checksum to the response
        request["checksum"] = checksum

        return request
