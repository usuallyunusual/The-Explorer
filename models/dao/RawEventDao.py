from etl.db import DatabaseUtil


class RawEventDao(DatabaseUtil):
    """
    Data Access Object defines operations on raw_event table in raw_explorer database
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def get_data(self, field):
        """
        Returns the result tuples of required data field from the raw_events table
        :param field: The required field(s). Can be a list or empty for all columns
        :type field: str
        :return: Tuples of the required data
        """
