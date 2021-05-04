class RawEventDao:
    """
    Data Access Object defines operations on raw_event table in raw_explorer database
    """

    def __init__(self, databaseUtil):
        """
        Constructor
        """
        self.databaseUtil = databaseUtil

    def get_data(self, field=None, limit=None, orderby=None):
        """
        Returns the result tuples of required data field from the raw_events table
        :param orderby: Order by a particular columns in table
        :param limit: Limit the number of responses
        :param field: The required field(s). Can be a list or empty for all columns
        :type field: str
        :return: Tuples of the required data
        """
        query = self.prepare_query(field, limit, orderby)
        conn = self.databaseUtil.get_connection()
        try:
            with conn.cursor() as cur:
                query_result = cur.execute(query)
                return query_result
        except Exception as e:
            print(e)

    def prepare_query(self, field=None, limit=None, orderby=None):
        """
        Prepares query string from parameters provided and returns the query string
        :param field: The field(s) to be queried in the table, None for all
        :param limit: The number of results to limit the query to
        :param orderby: Order by a certain field
        :return: String query
        """
        # If field is a sring (single field, convert it into a list
        if type(field) == str:
            field = [field]

        # Build the query
        query = "SELECT "
        if field is None:
            query += "* FROM raw_event"
        else:
            formatted_fields = ",".join(field)
            query += f"{formatted_fields} FROM raw_event"
        if limit is not None:
            query += f" LIMIT {limit}"
        if orderby is not None:
            query += f" ORDERBY {orderby}"
        return query
