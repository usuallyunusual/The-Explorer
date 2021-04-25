import os
from logging import getLogger, FileHandler, Formatter

from psycopg2 import connect, Error
from yaml import safe_load, YAMLError


class DatabaseUtil:
    """
    Utility class for common database functions.
    """

    def __init__(self, config_filename="config.yaml"):
        """
            Constructor initializes the logger
        """
        self.LOGGER = getLogger(__name__)
        handler = FileHandler("explorer.log")
        formatter = Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.config_filename = config_filename

    def get_connection(self):
        """
        Returns a psycopg2 connection object
        :return: psycop2g connection object
        """
        configs = self.get_db_config()
        try:
            return connect(
                "dbname={} user={} password={}".format(configs["db_name"], configs["db_user"], configs["db_pass"]))
        except Error as exc:
            self.LOGGER.exception("Exception occurred")

    def get_db_config(self):
        """
        Helper method to read configs from ".config.yaml" file.
        Throws exception if file does not exist
        :return: a dict of configs (username,password,db_name)
        :rtype: dict
        """
        print(os.path.dirname(os.path.realpath(__file__)) + self.config_filename)
        try:
            with open(os.path.dirname(os.path.realpath(__file__)) + "\\" + self.config_filename, 'r') as config_file:
                configs = safe_load(config_file)
            return configs
        except YAMLError as exc:
            self.LOGGER.exception("Exception occurred: " + repr(exc))
        except Exception as exc:
            self.LOGGER.exception("Exception occurred: " + repr(exc))
