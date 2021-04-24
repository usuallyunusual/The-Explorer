import unittest

from yaml import YAMLError

from etl.db.DatabaseUtil import DatabaseUtil


class TestDatabaseUtil(unittest.TestCase):

    def test_get_db_configs_normal_run(self):
        """
        Test the get_db_config method to see if YAML response is parsed correctly
        :return:
        """
        test_dict = {"db_name": "mydatabase", "db_user": "myusername", "db_pass": "mypassword"}
        result = DatabaseUtil("test_config.yaml").get_db_config()
        self.assertDictEqual(result, test_dict)

    def test_get_db_config_file_doesnt_exist(self):
        """
        Test whether function handles if file doesn't exist
        :return:
        """
        DatabaseUtil("non-existent-file").get_db_config()
        self.assertRaises(Exception)

    def test_get_db_config_bad_yaml(self):
        """
        Test whether function handles bad yaml string
        :return:
        """
        bad_yaml_string = """
        db_name something
        db_user : username"""
        DatabaseUtil(bad_yaml_string).get_db_config()
        self.assertRaises(YAMLError)

    def test_get_cursor(self):
        pass
