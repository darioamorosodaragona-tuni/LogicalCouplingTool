import os
import shutil
import unittest

import pandas
import pandas as pd
from neo4j import GraphDatabase
from neomodel import db
from git import Repo

from LogicalCouplingNoDb.src.developer_coupling import analyze_and_save_actual_commit


class TestDeveloperCoupling(unittest.TestCase):
    # Replace these values with your Neo4j database credentials and URI
    path = ".ProjectToTestLogicalCouplingTool"
    path_to_data = '../.data/.ProjectToTestLogicalCouplingTool/developer_coupling'

    def setUp(self):
        os.makedirs(self.path, exist_ok=True)
        repo = Repo.init(self.path)
        # repo = Repo(self.path)

        update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component1'):
            os.makedirs(f'{self.path}/component1')

        with open(f"{self.path}/{update_file_1}", "a") as f:
            f.write("\nUpdate version 2")

        add_file = [update_file_1]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Update to file2")

        path_to_data = '../.data/.ProjectToTestLogicalCouplingTool/developer_coupling'
        os.makedirs(path_to_data, exist_ok=True)

    def test_analyze_new_component(self):
        result__expected = pandas.DataFrame({'COMPONENT': [], 'DEVELOPER': []})

        actual_result = analyze_and_save_actual_commit(self.path, 'main', 'HEAD', [], [], [], self.path_to_data)

        self.assertTrue(result__expected.equals(actual_result))

    def test_analyze_existent_component(self):
        with open(f"{self.path_to_data}/component1", "w") as f:
            f.write("dev1")

        result__expected = pandas.DataFrame(
            {'COMPONENT': ['component1'], 'DEVELOPER': ['dario.amorosodaragona@tuni.fi']})

        actual_result = analyze_and_save_actual_commit(self.path, 'main', 'HEAD', [], [], ['component1'],
                                                       self.path_to_data)

        self.assertTrue(result__expected.equals(actual_result))

    def test_ignore_component(self):
        with open(f"{self.path_to_data}/component1", "w") as f:
            f.write("dev1")

        components_to_ignore = ['component1/*']

        result__expected = pandas.DataFrame(
            {'COMPONENT': [], 'DEVELOPER': []})

        actual_result = analyze_and_save_actual_commit(self.path, 'main', 'HEAD', components_to_ignore, [],
                                                       ['component1'], self.path_to_data)

        self.assertTrue(result__expected.equals(actual_result))

    def test_ignore_developer(self):
        with open(f"{self.path_to_data}/component1", "w") as f:
            f.write("dev1")

        dev_to_ignore = ['dario.amorosodaragona@tuni.fi']

        result__expected = pandas.DataFrame(
            {'COMPONENT': [], 'DEVELOPER': []})

        actual_result = analyze_and_save_actual_commit(self.path, 'main', 'HEAD', [], dev_to_ignore,
                                                       ['component1'], self.path_to_data)

        self.assertTrue(result__expected.equals(actual_result))

    def tearDown(self):
        shutil.rmtree('../.data/', ignore_errors=True)
        shutil.rmtree(self.path, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
