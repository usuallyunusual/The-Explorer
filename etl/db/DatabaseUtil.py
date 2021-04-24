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

    def get_connection(self, configs):
        """
        Returns a psycopg2 connection object
        :param configs: Dict of username, password and database name
        :return: psycop2g connection object
        """
        try:
            return connect(
                "dbname={} user={} pass={}".format(configs["db_name"], configs["db_user"], configs["db_pass"]))
        except Error as exc:
            self.LOGGER.exception("Exception occurred")

    def get_cursor(self):
        """
        Returns the cursor to perform operation on db
        :param config_filename: Name of the config file
        :type config_filename: str
        :return: psycopg2 cursor object
        """
        configs = self.get_db_config()
        connection = self.get_connection(configs)
        return connection.cursor()

    def get_db_config(self):
        """
        Helper method to read configs from ".config.yaml" file.
        Throws exception if file does not exist
        :return: a dict of configs (username,password,db_name)
        :rtype: dict
        """
        print(os.path.dirname(os.path.realpath(__file__)) + self.config_filename)
        try:
            configs = safe_load(open(os.path.dirname(os.path.realpath(__file__)) + "\\" + self.config_filename, 'r'))
            return configs
        except YAMLError as exc:
            self.LOGGER.exception("Exception occurred: " + repr(exc))
        except Exception as exc:
            self.LOGGER.exception("Exception occurred: " + repr(exc))
