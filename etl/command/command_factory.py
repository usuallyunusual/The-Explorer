from etl.command.decrypt_command import DecryptCommand
from etl.command.encrypt_command import EncryptCommand
from etl.command.raw_upload_command import RawUploadCommand


class CommandFactory:
    def __init__(self, args):
        self.factory_map = {
            "raw_upload": RawUploadCommand(args),
            "encrypt": EncryptCommand(args),
            "decrypt": DecryptCommand(args)
        }

    def get_command(self, command_name):
        return self.factory_map[command_name]
