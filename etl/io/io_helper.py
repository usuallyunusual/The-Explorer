import os
import shutil
import logging

from etl.counters import Counters


class IOHelper:
    __FILES_WRITTEN_TO_LOCAL_FS = "Number of files written to local FS"

    def __init__(self):
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def read(self, file_name):
        raise NotImplementedError("Whoops")

    def write(self, data, file_name):
        raise NotImplementedError("Whoops")

    def write_local_fs(self, data, filename):
        if os.path.exists(filename):
            raise RuntimeError(f"File {filename} already exists, not overwriting")
        dir = "/".join(filename.split("/")[:-2])
        if not os.path.exists(dir):
            raise RuntimeError(f"The directory {dir} path for the file does not exist, exiting.")
        timestamp = "/".join(filename.split("/")[:-1])
        if not os.path.exists(timestamp):
            os.makedirs(timestamp)
        self.LOGGER.info(f"Writing file {data} to destination {filename}")
        shutil.copyfile(data, filename)
        Counters.increment(self.__FILES_WRITTEN_TO_LOCAL_FS)
        return True

    def read_local_fs(self, filename):
        if not os.path.exists(filename):
            raise RuntimeError(f"File {filename} does not exist, exiting.")
        with open(filename, "r") as readfile:
            return readfile.read()
