import os
import unittest
import pandas as pd
from neo4j import GraphDatabase
from neomodel import db

import src.DBManager as DBManager
from LogicalCouplingNoDb.src.main import update_data, alert, save, initialize, load_previuos_results


class TestCalculator(unittest.TestCase):
    # Replace these values with your Neo4j database credentials and URI

    def test_analyze_actual_commit(self):


    def test_data_update(self):
        data1 = {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'B'], 'LC_VALUE': [1, 1]}
        data2 = {'COMPONENT 1': ['A', 'C', 'F'], 'COMPONENT 2': ['B', 'D', 'A'], 'LC_VALUE': [1, 7, 3]}
        result = {'COMPONENT 1': ['A', 'B', 'C', 'F'], 'COMPONENT 2': ['B', 'B', 'D', 'A'], 'LC_VALUE': [2, 1, 7, 3]}

        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        df_result = pd.DataFrame(result)
        actual_result = update_data(df1, df2)
        self.assertTrue(df_result.equals(actual_result), "Data update failed.")



if __name__ == '__main__':
    unittest.main()
