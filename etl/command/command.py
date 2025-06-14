import logging
import argparse

from etl.command.command_factory import CommandFactory
from etl.counters import Counters


class Command:
    def __init__(self, args):
        self.args = vars(args)
        logging.basicConfig(level=self.args["log_level"])
        self.LOGGER = logging.getLogger(__name__)

    def run(self):
        CommandFactory(self.args).get_command(self.args["command"]).run()
        self.show_counters()

    def show_counters(self):
        for key, value in Counters.get_all_counters().items():
            self.LOGGER.info(f"{key}: {value}")


if __name__ == "__main__":
    parent_parser = argparse.ArgumentParser("Explorer ETL CLI")
    sub_parser = parent_parser.add_subparsers(help="Sub Commands", dest="command", required=True)

    # Raw Upload Command
    raw_upload_parser = sub_parser.add_parser("raw_upload")
    raw_upload_parser.add_argument("-c", "--config", help="The config file path to read data from", required=True)
    raw_upload_parser.add_argument("-k", "--encryption-key", help="The key used to encrypt/decrypt secrets", required=True)
    raw_upload_parser.add_argument("-l", "--log-level", help="Log level", default="INFO")

    # Encrypt Command
    encrypt_parser = sub_parser.add_parser("encrypt")
    encrypt_parser.add_argument("-t", "--text", help="Text to crypt", required=True)
    encrypt_parser.add_argument("-k", "--encryption-key", help="Encryption key", required=True)
    encrypt_parser.add_argument("-l", "--log-level", help="Log level", default="INFO")

    # Decrypt command
    decrypt_parser = sub_parser.add_parser("decrypt")
    decrypt_parser.add_argument("-t", "--text", help="Text to crypt", required=True)
    decrypt_parser.add_argument("-k", "--encryption-key", help="Encryption key", required=True)
    decrypt_parser.add_argument("-l", "--log-level", help="Log level", default="INFO")

    args = parent_parser.parse_args()
    Command(args).run()
