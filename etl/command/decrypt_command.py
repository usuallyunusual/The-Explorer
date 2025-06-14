import logging

from etl.crypt.decrypt import Decrypt


class DecryptCommand:
    def __init__(self, args):
        self.args = args
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.LOGGER.info("Decrypt command")
        self.LOGGER.info(Decrypt(self.args["encryption_key"]).decrypt(self.args["text"]).decode())
