import os
import unittest
import pandas as pd
from neo4j import GraphDatabase
from neomodel import db

from coupling.logical_coupling import (update_data, alert, save, load_previous_results)

@unittest.skip("Skipping Neo4j tests beacuse not implemented yet")
class TestData(unittest.TestCase):


    # Replace these values with your Neo4j database credentials and URI

    def test_data_update(self):
        data1 = {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'B'], 'LC_VALUE': [1, 1]}
        data2 = {'COMPONENT 1': ['A', 'C', 'F'], 'COMPONENT 2': ['B', 'D', 'A'], 'LC_VALUE': [1, 7, 3]}
        result = {'COMPONENT 1': ['A', 'B', 'C', 'F'], 'COMPONENT 2': ['B', 'B', 'D', 'A'], 'LC_VALUE': [2, 1, 7, 3]}

        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        df_result = pd.DataFrame(result)
        actual_result = update_data(df1, df2)
        self.assertTrue(df_result.equals(actual_result), "Data update failed.")

    def test_alert(self):
        data1 = {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'B'], 'LC_VALUE': [1, 1]}
        data2 = {'COMPONENT 1': ['A', 'C', 'F'], 'COMPONENT 2': ['B', 'D', 'A'], 'LC_VALUE': [1, 7, 3]}
        result = {'COMPONENT 1': ['A', 'B', 'C', 'F'], 'COMPONENT 2': ['B', 'B', 'D', 'A'], 'LC_VALUE': [2, 1, 7, 3]}
        expected = {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'B'], 'NEW_LC_VALUE': [2, 1],'OLD_LC_VALUE': [1, 0]}

        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)

        df_result = pd.DataFrame(result)
        increasing = alert(df1, df2)
        df_expected = pd.DataFrame(expected)
        increasing['OLD_LC_VALUE'] = increasing['OLD_LC_VALUE'].astype(int)
        increasing['NEW_LC_VALUE'] = increasing['NEW_LC_VALUE'].astype(int)
        self.assertTrue(df_expected.equals(increasing), "Data update failed.")


    def test_save(self):
        data1 = {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'B'], 'LC_VALUE': [1, 1]}
        df1 = pd.DataFrame(data1)
        os.makedirs(f'../.data/test', exist_ok=True)
        save(df1, 'test')
        self.assertTrue(os.path.exists(f'../.data/test/LogicalCoupling.csv'), "Save failed.")
        os.remove(f'../.data/test/LogicalCoupling.csv')
        os.rmdir(f'../.data/test')
        os.rmdir('../.data')

    def test_initialize(self):
        # initialize()
        self.assertTrue(os.path.exists('../.data'), "Initialize failed.")
        # self.assertTrue(os.path.exists('../.temp'), "Initialize failed.")
        os.rmdir('../.data')
        # os.rmdir('../.temp')

    def test_load_data(self):
        data1 = {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'B'], 'LC_VALUE': [1, 1]}
        df1 = pd.DataFrame(data1)
        os.makedirs(f'../.data/test', exist_ok=True)
        df1.to_csv(f'../.data/test/LogicalCoupling.csv', index=False)
        loaded = load_previous_results('test', )
        self.assertTrue(df1.equals(loaded), "Load failed.")
        os.remove(f'../.data/test/LogicalCoupling.csv')
        os.rmdir(f'../.data/test')
        os.rmdir('../.data')

    def test_no_previous_results(self):
        data1 = {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'B'], 'LC_VALUE': [1, 1]}
        df1 = pd.DataFrame(data1)
        os.makedirs(f'../.data/test', exist_ok=True)
        df1.to_csv(f'../.data/test/LogicalCoupling.csv', index=False)

        loaded = load_previous_results('test_main', )
        expected_results = pd.DataFrame(columns=['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE'])

        self.assertTrue(expected_results.equals(loaded), "Load failed.")
        os.remove(f'../.data/test/LogicalCoupling.csv')
        os.rmdir(f'../.data/test_main')
        os.rmdir(f'../.data/test')
        os.rmdir('../.data')


if __name__ == '__main__':
    unittest.main()
