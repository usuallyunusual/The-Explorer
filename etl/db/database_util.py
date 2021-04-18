from logging import getLogger, FileHandler, Formatter

from psycopg2 import connect
from yaml import safe_load, YAMLError


class databaseUtil:
    """
    Utility class for common database functions.
    """

    def __init__(self):
        """
            Constructor initializes the logger
        """
        self.LOGGER = getLogger(__name__)
        handler = FileHandler("explorer.log")
        formatter = Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

    def get_connection(self, db_name, configs):
        """
        Returns a psycopg2 connection object
        :param db_name:
        :type db_name:str
        :return: psycop2g connection object
        """
        return connect("dbname={} user={} pass={}".format(db_name, configs["db_user"], configs["db_pass"]))

    # Define getting connection here

    def get_cursor(self, db_name):
        """
        Returns the cursor to perform operation on db
        :param db_name: Name of the database
        :type db_name: str
        :return: psycopg2 cursor object
        """
        configs = self.get_db_config()
        connection = self.get_connection(db_name, configs)
        return connection.cursor()

    def get_db_config(self):
        """
        Helper method to read configs from ".config.yaml" file.
        Throws exception if file does not exist
        :return: a dict of configs (username,password)
        :rtype: dict
        """
        try:
            configs = safe_load("config.yaml")
            return configs
        except YAMLError as exc:
            self.LOGGER.exception("Exception occurred")
