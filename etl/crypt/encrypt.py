from cryptography.fernet import Fernet
import logging

class Encrypt:

    def __init__(self, encryption_key):
        self.encryption_key = encryption_key
        self.fernet = Fernet(self.encryption_key)
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def encrypt(self, text):
        self.LOGGER.info(f"Encrypting {text}")
        return self.fernet.encrypt(text.encode("utf-8"))
