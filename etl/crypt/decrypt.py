from cryptography.fernet import Fernet
import logging

class Decrypt:

    def __init__(self, encryption_key):
        self.encryption_key = encryption_key
        self.fernet = Fernet(self.encryption_key)
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def decrypt(self, text):
        self.LOGGER.info(f"Decrypting {text}")
        return self.fernet.decrypt(text.encode("utf-8"))
