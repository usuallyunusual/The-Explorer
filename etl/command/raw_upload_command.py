import logging

from etl.crypt.decrypt import Decrypt
from etl.raw_upload.raw_upload import RawUpload


class RawUploadCommand:
    def __init__(self, args):
        self.LOGGER = logging.getLogger(__name__)
        self.args = args

    def run(self):
        self.LOGGER.info("Running RawUpload Command")
        RawUpload(self.args["config"], Decrypt(self.args["encryption_key"])).raw_upload()


