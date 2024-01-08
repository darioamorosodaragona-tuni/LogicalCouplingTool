import unittest
from neo4j import GraphDatabase
from neomodel import db

import src.DBManager as DBManager

class TestDatabaseConnection(unittest.TestCase):
    # Replace these values with your Neo4j database credentials and URI
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "cable-convert-native-radio-mailbox-1174"

    def test_database_connection(self):
        DBManager.connect_to_db(url='localhost', port='7687', username=self.username, password=self.password)
        # Check if the database exists
        connected = db.cypher_query("RETURN 1")[0][0][0]

        # Assert the result
        self.assertEqual(1, connected, "Connection to Neo4j failed.")


if __name__ == '__main__':
    unittest.main()
