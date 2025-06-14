from etl.crypt.encrypt import Encrypt
import logging


class EncryptCommand:
    def __init__(self, args):
        self.args = args
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.LOGGER.info("Encrypt command")
        self.LOGGER.info(Encrypt(self.args["encryption_key"]).encrypt(self.args["text"]).decode())
