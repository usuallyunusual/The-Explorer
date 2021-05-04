import unittest

from etl.db.DatabaseUtil import DatabaseUtil
from models.dao.RawEventDao import RawEventDao


class TestRawEventDao(unittest.TestCase):
    """
    Test the RawEventDao class
    """

    def test_prepare_query(self):
        """
        Tests the prepare_query method to see if it returns
        appropriate strings
        """
        # Test object
        raweventdao = RawEventDao("someobj")

        # All params are None
        query_string = raweventdao.prepare_query()
        self.assertEqual("SELECT * FROM raw_event", query_string)

        # Single field is given, limit and orderby is None
        query_string = raweventdao.prepare_query("html")
        self.assertEqual("SELECT html FROM raw_event", query_string)

        # Multiple field is given, limit and orderby is None
        query_string = raweventdao.prepare_query(["html", "raw_event_id"])
        self.assertEqual("SELECT html,raw_event_id FROM raw_event", query_string)

        # Limit is given no fields or orderby
        query_string = raweventdao.prepare_query(limit=5)
        self.assertEqual("SELECT * FROM raw_event LIMIT 5", query_string)

        # orderby is given no fields or limit
        query_string = raweventdao.prepare_query(orderby="raw_event_id")
        self.assertEqual("SELECT * FROM raw_event ORDERBY raw_event_id", query_string)

        # All params given
        query_string = raweventdao.prepare_query(["html", "raw_event_id"], 5, "raw_event_id")
        self.assertEqual("SELECT html,raw_event_id FROM raw_event LIMIT 5 ORDERBY raw_event_id", query_string)

    def test_get_data_bad_params(self):
        """
        Method should throw exception when params are bad, ex
        field doesn't exist, limit is a string or other such edge cases
        :return:
        """
        RawEventDao(DatabaseUtil()).get_data("hello")
        self.assertRaises(Exception)
