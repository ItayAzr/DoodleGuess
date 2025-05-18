from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

import os


class KeyManager:
    def __init__(self, private_key_path="private_key.pem", public_key_path="public_key.pem",):
        """
        :param private_key_path: Path to the private key file
        :param public_key_path: Path to the public key file
        """
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self.__private_key = None
        self.__public_key = None

    def generate_keys(self, key_size=2048):
        """
        Generate a new RSA private/public key pair.
        Saves the generated keys to disk.
        """
        print("Generating new RSA key pair...")
        self.__private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        self.__public_key = self.__private_key.public_key()
        self.save_keys()
        self.load_keys()

    def save_keys(self):
        """
        Save both private and public keys to disk in PEM format.
        Encrypts the private key if a password was provided.
        """
        if self.__private_key is None or self.__public_key is None:
            raise ValueError("Keys must be generated or loaded before saving.")

        # Save the private key to a file
        with open(self.private_key_path, "wb") as f:
            f.write(self.__private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save the public key to a file (not encrypted)
        with open(self.public_key_path, "wb") as f:
            f.write(self.__public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))


    def load_keys(self):
        """
        Load keys from the disk. If files do not exist, generate new ones.
        """
        if not os.path.exists(self.private_key_path) or not os.path.exists(self.public_key_path):
            print("Key files not found. Generating new keys...")
            self.generate_keys()
            return

        # Load the private key from file, using the password if needed
        with open(self.private_key_path, "rb") as f:
            self.__private_key = serialization.load_pem_private_key(f.read(), password=None)

        # Load the public key from file
        with open(self.public_key_path, "rb") as f:
            self.__public_key = f.read().decode('utf-8')

    def decypher_aes_key(self, encrypted_key):
        key = self.__private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return key

    def get_private_key(self):
        """
        Return the private key object. Load it if not already loaded.
        """
        if self.__private_key is None:
            self.load_keys()
        return self.__private_key

    def get_public_key(self):
        """
        Return the public key object. Load it if not already loaded.
        """
        if self.__public_key is None:
            self.load_keys()
        return self.__public_key
