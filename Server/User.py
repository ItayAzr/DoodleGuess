import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import socket
import json
import hashlib
import struct
import os


class User:
    def __init__(self, address: tuple, con: socket.socket, **data):
        """
        Client interface for organized collection of the client data with the connection.
        :param address: the address of the client
        :param con: the socket connection with the client
        :param data: other data that connected to the client, the data will be saved in the data collection.
        """
        self.lobby = None
        self.connection = con
        self.address = address
        self.data = data
        self.data['username'] = 'Guest'
        self.data['logged_in'] = False

    def encrypt_message(self, request: dict):
        """
        Encrypts a Python dictionary as JSON using AES-GCM.
        Returns a base64-encoded string of nonce + ciphertext + tag.
        """
        try:
            aes_gcm = AESGCM(self.data['aes_key'])
            nonce = os.urandom(12)  # GCM nonce must be 12 bytes

            # Convert dict to JSON string, then to bytes
            json_data = json.dumps(request).encode("utf-8")

            # Encrypt (ciphertext includes the 16-byte tag at the end)
            ciphertext = aes_gcm.encrypt(nonce, json_data, associated_data=None)

            # Concatenate nonce + ciphertext and base64-encode it
            encrypted = base64.b64encode(nonce + ciphertext).decode("utf-8")
            return encrypted
        except Exception as e:
            print(e)
            return None

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
        aes_gcm = AESGCM(self.data['aes_key'])
        json_data = aes_gcm.decrypt(nonce, ciphertext_and_tag, associated_data=None)

        # Parse JSON back to dict
        return json.loads(json_data.decode("utf-8"))

    def get_data(self, name: str):
        """
        Get a specific key from the data collection.
        :param name: the key of the data value
        :return: the value of the key in the data collection
        """
        if name in self.data:
            return self.data[name]

        return None

    def set_data(self, name: str, value: any):
        """
        Set a specific data to the data collection.
        :param name: the key of the data value.
        :param value: the value of the key that will be saved in the data collection.
        :return: the success of the operation.
        """
        self.data[name] = value

    # ensures that all the data is received
    def recv_all(self, length):
        try:
            data = b''
            while len(data) < length:
                chunk = self.connection.recv(length - len(data))
                if not chunk:
                    return None  # connection closed
                data += chunk
            return data
        except Exception as e:
            print(e)

    # receives requests from client
    def get_request(self, game_request=False) -> dict or None:
        try:
            if game_request:
                request_data = self.connection.recv(1024)
                request = json.loads(request_data.decode())
                return request
            else:
                # Step 1: Receive the message length (4 bytes)
                msg_length_data = self.recv_all(4)
                if not msg_length_data:
                    print("Connection closed before receiving length")
                    return None

                msg_length = struct.unpack("!I", msg_length_data)[0]  # Convert 4 bytes to integer
                print(f"Expecting {msg_length} bytes...")

                # Step 2: Receive the complete JSON message
                data = self.recv_all(msg_length)

                if data is None:
                    return None
                print(type(data))

                if 'aes_key' in self.data.keys():
                    request = self.decrypt_message(data)
                else:
                    request = json.loads(data.decode('utf-8'))
                print(f'request: {request}')

                if 'checksum' not in request.keys():
                    self.send_response("Bad Request", 'missing checksum value')
                else:
                    checksum = request['checksum']
                    request.pop('checksum')
                    current_checksum = hashlib.sha256(json.dumps(request).encode()).hexdigest()
                    if current_checksum == checksum:
                        return request
                    else:
                        self.send_response("Bad Request", 'incomplete request')

        except ConnectionResetError:
            # if the connection is reset, return None
            return None

        except Exception as e:
            # print the exception
            print(e)
            if not game_request:
                # send an error response
                self.send_response("Bad Request", 'oops, something went wrong')

            return None

    def send_response(self, status: str = 'response', msg: str = 'data sent',  data: dict = None,):
        """
        :param status: request status
        :param msg: message for the client
        :param data: the content of the response
         if : initial rsa exchange was completed and server has AES key,
         sends a crypted request. if not: server does not have AES key, sends a non-crypted request
        :return:
        """
        try:
            if data is None:
                data = {}
            # group all the response (except the checksum) into a json to calc the checksum.
            response = {"status": status, 'data': data}

            response['data']['msg'] = msg

            # calc the checksum
            checksum = hashlib.sha256(json.dumps(response).encode('utf-8')).hexdigest()

            # add the checksum to the response
            response["checksum"] = checksum
            print('sent response to ' + self.get_data('username'))
            print(f'response {response} \n')
            if 'aes_key' not in self.data.keys():
                response = json.dumps(response).encode('utf-8')
            else:
                response = self.encrypt_message(response).encode('utf-8')

            # Send the message length first (4 bytes)
            self.connection.send(struct.pack("!I", len(response)))

            # Send the response to the client.
            self.connection.sendall(response)

        except Exception as e:
            # print the exception
            print(e)

            return False

    def send_game_data(self, data):
        self.connection.sendall(json.dumps(data).encode('utf-8'))
