import unittest
import tempfile
import shutil
import os
import pandas as pd
from unittest.mock import patch
from io import StringIO
from datetime import datetime

from LogicalCouplingNoDb.src.logical_coupling import load_previous_results, analyze_commits, convertToNumber, \
    convertFromNumber, update_data, alert, alert_messages, save, run

from ...src.util import clone
from ...src.logical_coupling import run
class TestLogicalCouplingTool(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        # Remove the temporary directory after testing
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree('.data', ignore_errors=True)

    def test_load_previous_results(self):
        # Create a dummy .lcignore file for testing
        with open('.lcignore', 'w') as lcignore_file:
            lcignore_file.write('ignore_me.txt\n')

        # Create a dummy .data folder
        os.makedirs('.data/repo_name', exist_ok=True)

        # Test with existing data
        data, components_to_ignore, commits_analyzed = load_previous_results('repo_name', self.temp_dir, 'main')

        self.assertEqual(len(data.columns), 3)
        self.assertEqual(len(components_to_ignore), 1)
        self.assertEqual(len(commits_analyzed.columns), 1)

        # Test without existing data
        shutil.rmtree('.data/repo_name', ignore_errors=True)
        data, components_to_ignore, commits_analyzed = load_previous_results('repo_name', self.temp_dir, 'main')

        self.assertEqual(len(data.columns), 3)
        self.assertEqual(len(components_to_ignore), 1)
        self.assertEqual(len(commits_analyzed.columns), 1)

    def test_analyze_commits(self):
        # Mock the Repository class from pydriller
        with patch('your_module_name.pydriller.Repository') as mock_repository:
            mock_repository_instance = mock_repository.return_value
            mock_repository_instance.traverse_commits.return_value = [
                {'hash': 'abc', 'modified_files': [MockFile('file1.txt'), MockFile('file2.py')]},
                {'hash': 'def', 'modified_files': [MockFile('file2.py'), MockFile('file3.py')]}
            ]

            # Test with last_commit_analyzed being None
            new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', ['abc', 'def'], None, [])

            self.assertEqual(len(new_data.columns), 3)
            self.assertEqual(len(new_commits_analyzed), 2)

            # Test with last_commit_analyzed being 'abc'
            new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', ['abc', 'def'], 'abc', [])

            self.assertEqual(len(new_data.columns), 3)
            self.assertEqual(len(new_commits_analyzed), 1)

    def test_convertToNumber(self):
        result = convertToNumber('test_string')
        self.assertEqual(result, 18237106760400441668)

    def test_convertFromNumber(self):
        result = convertFromNumber(18237106760400441668)
        self.assertEqual(result, 'test_string')

    def test_update_data(self):
        # Create dummy dataframes
        data = pd.DataFrame({'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [1, 2]})
        new_data = pd.DataFrame({'COMPONENT 1': ['B', 'C'], 'COMPONENT 2': ['D', 'E'], 'LC_VALUE': [3, 4]})

        # Test the update_data function
        merged_data = update_data(data, new_data)

        self.assertEqual(len(merged_data), 4)
        self.assertEqual(merged_data.iloc[0]['LC_VALUE'], 1)
        self.assertEqual(merged_data.iloc[3]['LC_VALUE'], 4)

    def test_alert(self):
        # Create dummy dataframes
        previous_data = pd.DataFrame({'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [1, 2]})
        data_extracted = pd.DataFrame(
            {'COMPONENT 1': ['B', 'C'], 'COMPONENT 2': ['D', 'E'], 'LC_VALUE': [3, 4], 'COMMIT': ['abc', 'def']})

        # Test the alert function
        alert_data = alert(data_extracted, previous_data)

        self.assertEqual(len(alert_data), 2)
        self.assertEqual(alert_data.iloc[0]['NEW_LC_VALUE'], 1)
        self.assertEqual(alert_data.iloc[1]['OLD_LC_VALUE'], 0)

    def test_alert_messages(self):
        # Create a dummy dataframe
        increasing_data = pd.DataFrame({
            'COMPONENT 1': ['A', 'B'],
            'COMPONENT 2': ['B', 'C'],
            'NEW_LC_VALUE': [7, 4],
            'OLD_LC_VALUE': [1, 2],
            'COMMIT': ['abc', 'def']
        })

        # Test the alert_messages function
        message = alert_messages(increasing_data)

        self.assertIn('Commit abc:', message)
        self.assertIn('The components  A and B are coupled: 7', message)
        self.assertIn('Logical coupling between B and C increased from 2 to 4', message)

    def test_save(self):
        os.makedirs('.data/repo_name', exist_ok=True)
        # Create a dummy dataframe
        data = pd.DataFrame({'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [1, 2]})
        new_commits_analyzed = ['abc', 'def']
        commits_analyzed = pd.DataFrame({'COMMITS ANALYZED': ['xyz']})

        # Test the save function
        save(data, 'repo_name', new_commits_analyzed, commits_analyzed)

        # Check if the files are created and contain the expected data
        self.assertTrue(os.path.exists('.data/repo_name/LogicalCoupling.csv'))
        self.assertTrue(os.path.exists('.data/repo_name/analyzed.csv'))

        saved_data = pd.read_csv('.data/repo_name/LogicalCoupling.csv')
        saved_commits_analyzed = pd.read_csv('.data/repo_name/analyzed.csv')

        self.assertEqual(len(saved_data), 2)
        self.assertEqual(len(saved_commits_analyzed), 3)

    def test_run(self):
        # Mock the clone function
        with patch('..src.util.clone') as mock_clone:
            mock_clone.return_value = self.temp_dir

            # Test the run function
            exit_code, messages, _ = run('https://github.com/example/repo.git', 'main', 'abc')

            self.assertEqual(exit_code, 0)
            self.assertEqual(messages, "")
            # Add more assertions based on the expected behavior of the run function


# Helper class to mock PyDriller's ModifiedFile
class MockFile:
    def __init__(self, new_path):
        self.new_path = new_path


if __name__ == '__main__':
    unittest.main()
