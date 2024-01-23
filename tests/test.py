import unittest
import tempfile
import shutil
import os
from importlib import reload

import pandas
import pandas as pd
from unittest.mock import patch, Mock
from io import StringIO
from datetime import datetime
import pydriller
from git import Repo

from coupling.logical_coupling import load_previous_results, analyze_commits, convertToNumber, \
    convertFromNumber, update_data, alert, alert_messages, save, run

from coupling import util




class TestLogicalCouplingTool(unittest.TestCase):
    current_dir = None
    temp_dir = None

    @classmethod
    def setUpClass(cls):

        # Create a temporary directory for testing
        cls.temp_dir = tempfile.mkdtemp()
        cls.current_dir = os.getcwd()
        os.chdir(cls.temp_dir)

    def setUp(self):
        self.__class__.temp_dir = tempfile.mkdtemp()
        os.chdir(self.__class__.temp_dir)

    def tearDown(self):
        # Remove the temporary directory after testing
        temp_dir = self.__class__.temp_dir

        os.chdir(self.__class__.current_dir)

        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree('.data', ignore_errors=True)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.current_dir)

    def create_commits(self, components_nfile: dict, order=[], coupling: [] = []):
        os.makedirs(self.temp_dir, exist_ok=True)
        repo = Repo.init(self.temp_dir)
        commits_hashes = []
        # repo = Repo(self.path)

        files_updated = []

        for component_name in components_nfile.keys():
            n_files = components_nfile[component_name]
            for i in range(n_files):
                update_file = f"{component_name}/{i}.py"
                files_updated.append(update_file)
                if not os.path.exists(f'{self.temp_dir}/{component_name}'):
                    os.makedirs(f'{self.temp_dir}/{component_name}')
                with open(f"{self.temp_dir}/{update_file}", "a") as f:
                    f.write("\nUpdate version 2")

        to_commit = []
        if coupling:
            for coupling_pair in coupling:
                commits_add_file = []
                for file in files_updated.copy():
                    if coupling_pair[0] in file or coupling_pair[1] in file:
                        commits_add_file.append(file)
                        files_updated.remove(file)
                to_commit.append(commits_add_file)
                # repo.index.add(commits_add_file)
                # commits_hashes.append(repo.index.commit("Update to file2").hexsha)

        for file in files_updated:
            add_file = [file]
            to_commit.append(add_file)

        for com in order:
            for commit in to_commit:
                if com in commit[0]:
                    repo.index.add(commit)
                    to_commit.remove(commit)
                    commits_hashes.append(repo.index.commit("Update to file2").hexsha)

        if coupling:
            return commits_hashes

    def test_load_previous_results_previous_results(self):
        # Create a dummy .lcignore file for testing
        with open('.lcignore', 'w') as lcignore_file:
            lcignore_file.write('ignore_me.txt\n')

        # Create a dummy .data folder
        os.makedirs('.data/repo_name', exist_ok=True)

        with open('.data/repo_name/LogicalCoupling.csv', 'w') as data_file:
            data_file.write('COMPONENT 1,COMPONENT 2,LC_VALUE\n')
            data_file.write('A,B,1\n')
            data_file.write('B,C,2\n')

        with open('.data/repo_name/analyzed.csv', 'w') as analyzed_file:
            analyzed_file.write('COMMITS ANALYZED\n')
            analyzed_file.write('abc\n')
            analyzed_file.write('def\n')

        with patch("coupling.util.checkout") as mock_checkout:
            mock_checkout.return_value = None

            # Test with existing data
            data, components_to_ignore, commits_analyzed = load_previous_results('repo_name', self.temp_dir, 'main')

            self.assertEqual(len(data.columns), 3)
            self.assertTrue(
                data.equals(pd.DataFrame({'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [1, 2]})))
            self.assertTrue(components_to_ignore == ['ignore_me.txt', '.lcignore'])
            self.assertTrue(commits_analyzed.equals(pd.DataFrame({'COMMITS ANALYZED': ['abc', 'def']})))
            self.assertEqual(len(components_to_ignore), 2)
            self.assertEqual(len(commits_analyzed.columns), 1)

            # Clean
            shutil.rmtree('.data/repo_name', ignore_errors=True)

    def test_load_previous_results_no_previous_results(self):

        with patch("coupling.util.checkout") as mock_checkout:
            mock_checkout.return_value = None

            data, components_to_ignore, commits_analyzed = load_previous_results('repo_name', self.temp_dir, 'main')

            self.assertTrue(os.path.exists('.data/repo_name/'))
            self.assertTrue("COMMITS ANALYZED" in commits_analyzed.columns)
            self.assertEqual(len(data.columns), 3)
            self.assertEqual(len(components_to_ignore), 0)
            self.assertEqual(len(commits_analyzed.columns), 1)


        shutil.rmtree('.data/repo_name', ignore_errors=True)
    def test_load_previous_results_no_previous_results_no_data(self):

        with patch("coupling.util.checkout") as mock_checkout:
            mock_checkout.return_value = None

            self.original_exists = os.path.exists

            with patch("os.path.exists", autospec=os.path.exists, side_effect=self.analyzed_custom_exists):
                with patch("pandas.read_csv") as pansa_mock:
                    pansa_mock.return_value = pandas.DataFrame(columns=['COMMITS ANALYZED'])
                    # Test with existing data
                    data, components_to_ignore, commits_analyzed = load_previous_results('repo_name', self.temp_dir, 'main')

                    self.assertTrue(os.path.exists('.data/repo_name/'))
                    self.assertEqual(len(data.columns), 3)
                    self.assertEqual(len(components_to_ignore), 0)
                    self.assertEqual(len(commits_analyzed.columns), 1)


        shutil.rmtree('.data/repo_name', ignore_errors=True)


    def test_load_previous_results_no_previous_results_no_analyzed(self):

        with patch("coupling.util.checkout") as mock_checkout:
            mock_checkout.return_value = None

            self.original_exists = os.path.exists

            with patch("os.path.exists", autospec=os.path.exists, side_effect=self.data_custom_exists):
                with patch("pandas.read_csv") as pansa_mock:
                    pansa_mock.return_value = pandas.DataFrame()
                    # Test with existing data
                    data, components_to_ignore, commits_analyzed = load_previous_results('repo_name', self.temp_dir, 'main')

                    self.assertTrue(os.path.exists('.data/repo_name/'))
                    self.assertEqual(len(components_to_ignore), 0)
                    self.assertEqual(len(commits_analyzed.columns), 1)


        shutil.rmtree('.data/repo_name', ignore_errors=True)



    def analyzed_custom_exists(self, path):
            # Check if the path is the specific one you want to handle differently
        if "analyzed.csv" in path:
            # Handle the specific case
            return True
        else:
            # For other paths, delegate to the actual os.path.exists
            return self.original_exists(path)
    def data_custom_exists(self, path):
            # Check if the path is the specific one you want to handle differently
        if "LogicalCoupling" in path:
            # Handle the specific case
            return True
        else:
            # For other paths, delegate to the actual os.path.exists
            return self.original_exists(path)


    def test_analyze_commits(self):
        # Mock the Repository class from pydriller
        with patch('pydriller.Repository') as mock_repository:
            # Create a custom commit object for testing
            commit_mock1 = Mock(hash='abc', modified_files=[MockFile('file1.txt'), MockFile('file2.py')])
            commit_mock2 = Mock(hash='def', modified_files=[MockFile('file2.py'), MockFile('file3.py')])
            commit_mock3 = Mock(hash='ghi', modified_files=[MockFile('file4.py'), MockFile('file5.py')])

            mock_repository_instance = mock_repository.return_value
            mock_repository_instance.traverse_commits.return_value = [commit_mock1, commit_mock2, commit_mock3]

            # Test with last_commit_analyzed being None
            new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', ['abc', 'def', 'ghi'], None, [])

            self.assertEqual(len(new_data.columns), 4)
            self.assertEqual(len(new_commits_analyzed), 3)

    def test_analyze_commits_no_new_path(self):
        # Mock the Repository class from pydriller
        with patch('pydriller.Repository') as mock_repository:
            # Create a custom commit object for testing
            commit_mock1 = Mock(hash='abc', modified_files=[MockFile('file1.txt'), MockFile('file2.py')])
            commit_mock2 = Mock(hash='def', modified_files=[MockFile('file2.py'), MockFileNoNewPath()])
            mock_repository_instance = mock_repository.return_value
            mock_repository_instance.traverse_commits.return_value = [commit_mock1, commit_mock2]

            # Test with last_commit_analyzed being None
            new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', ['abc', 'def'], None, [])

            self.assertEqual(len(new_data.columns), 4)
            self.assertEqual(len(new_commits_analyzed), 2)
    def test_analyze_commits_no_new_path_2(self):
        # Mock the Repository class from pydriller
        with patch('pydriller.Repository') as mock_repository:
            # Create a custom commit object for testing
            commit_mock1 = Mock(hash='def', modified_files=[MockFile('file1.txt'), MockFileNoNewPath(), MockFile('file3.py')])
            mock_repository_instance = mock_repository.return_value
            mock_repository_instance.traverse_commits.return_value = [commit_mock1]

            # Test with last_commit_analyzed being None
            new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', ['def'], None, [])

            self.assertEqual(len(new_data.columns), 4)
            self.assertEqual(len(new_commits_analyzed), 1)
            self.assertEqual(len(new_data['LC_VALUE']), 1)
            self.assertEqual(new_data['LC_VALUE'][0], 1)
            self.assertEqual(new_data['COMPONENT 1'][0], 'file3.py')
            self.assertEqual(new_data['COMPONENT 2'][0], 'file1.txt')

    def test_analyze_commits_with_last_commit_no_coupling(self):

        os.makedirs(self.temp_dir, exist_ok=True)
        repo = Repo.init(self.temp_dir)
        # repo = Repo(self.path)

        update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.temp_dir}/component1'):
            os.makedirs(f'{self.temp_dir}/component1')

        with open(f"{self.temp_dir}/{update_file_1}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_2 = "component2/B.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.temp_dir}/component2'):
            os.makedirs(f'{self.temp_dir}/component2')

        with open(f"{self.temp_dir}/{update_file_2}", "a") as f:
            f.write("\nUpdate version 2")

        add_file = [update_file_1, update_file_2]  # relative path from git root
        repo.index.add(add_file)
        last_commit_analyzed = repo.index.commit("Update to file2").hexsha

        update_file_3 = "component1/C.py"  # we'll use local_dir/dir1/file2.txt

        with open(f"{self.temp_dir}/{update_file_3}", "a") as f:
            f.write("\nUpdate version 1")

        add_file = [update_file_3]  # relative path from git root
        repo.index.add(add_file)
        commit_to_analyze = repo.index.commit("Commit 2").hexsha

        new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main',
                                                         [commit_to_analyze, last_commit_analyzed],
                                                         last_commit_analyzed, [])

        self.assertTrue(new_data.empty)
        self.assertEqual(len(new_data.columns), 0)
        self.assertEqual(len(new_commits_analyzed), 1)

    def test_analyze_commits_with_last_commit_coupling(self):

        commits_to_analyze = self.create_commits({'A': 1, 'B': 2, 'C': 3}, ['A', 'B', 'C'], [('B', 'C')])

        new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', commits_to_analyze,
                                                         commits_to_analyze[0], [])

        self.assertFalse(new_data.empty)
        self.assertEqual(new_data['LC_VALUE'][0], 1)
        self.assertEqual(len(new_data.columns), 4)
        self.assertEqual(len(new_commits_analyzed), 1)
        self.assertEqual(len(new_data['LC_VALUE']), 1)
        self.assertEqual(new_data['LC_VALUE'][0], 1)
        self.assertEqual(new_data['COMPONENT 1'][0], 'B')
        self.assertEqual(new_data['COMPONENT 2'][0], 'C')

    def test_analyze_commits_coupling(self):

        commits_to_analyze = self.create_commits({'A': 1, 'B': 2, 'C': 3, 'D':1}, ['A', 'B', 'C', 'D'], [('B', 'C')])

        new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', commits_to_analyze, None, [])

        self.assertFalse(new_data.empty)
        self.assertEqual(new_data['LC_VALUE'][0], 1)
        self.assertEqual(len(new_data.columns), 4)
        self.assertEqual(len(new_commits_analyzed), 3)
        self.assertEqual(len(new_data['LC_VALUE']), 1)
        self.assertEqual(new_data['LC_VALUE'][0], 1)
        self.assertEqual(new_data['COMPONENT 1'][0], 'B')
        self.assertEqual(new_data['COMPONENT 2'][0], 'C')

    def test_analyze_commits_with_last_commit_coupling_to_ignore(self):

        commits_to_analyze = self.create_commits({'A': 1, 'B': 2, 'C': 3}, ['A', 'B', 'C'], [('B', 'C')])

        new_data, new_commits_analyzed = analyze_commits(self.temp_dir, 'main', commits_to_analyze,
                                                         commits_to_analyze[0], ["C/*"])

        self.assertTrue(new_data.empty)
        self.assertEqual(len(new_data.columns), 0)
        self.assertEqual(len(new_commits_analyzed), 1)


    def test_convertToNumber(self):
        result = convertToNumber('testString')
        self.assertEqual(result, 488440487847104619963764)

    def test_convertFromNumber(self):
        result = convertFromNumber(488440487847104619963764)
        self.assertEqual(result, 'testString')

    def test_update_data(self):
        # Create dummy dataframes
        data = pd.DataFrame({'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [1, 2]})
        new_data = pd.DataFrame({'COMPONENT 1': ['B', 'C'], 'COMPONENT 2': ['D', 'E'], 'LC_VALUE': [3, 4]})

        # Test the update_data function
        merged_data = update_data(data, new_data)

        self.assertEqual(len(merged_data), 4)
        self.assertEqual(merged_data.iloc[0]['LC_VALUE'], 1)
        self.assertEqual(merged_data.iloc[3]['LC_VALUE'], 4)

    def test_alert_new_rows(self):
        # Create dummy dataframes
        previous_data = pd.DataFrame({'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [1, 2]})
        data_extracted = pd.DataFrame(
            {'COMPONENT 1': ['B', 'C'], 'COMPONENT 2': ['D', 'E'], 'LC_VALUE': [3, 4], 'COMMIT': ['abc', 'def']})

        # Test the alert function
        alert_data = alert(data_extracted, previous_data)

        self.assertEqual(len(alert_data), 2)
        self.assertTrue({"B", "C"}.issubset(set(alert_data['COMPONENT 1'].tolist())))
        self.assertTrue({"D", "E"}.issubset(set(alert_data['COMPONENT 2'].tolist())))

        self.assertEqual(alert_data.iloc[0]['NEW_LC_VALUE'], 1)
        self.assertEqual(alert_data.iloc[1]['OLD_LC_VALUE'], 0)

    def test_alert_update_rows(self):
        # Create dummy dataframes
        previous_data = pd.DataFrame({'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [1, 2]})
        data_extracted = pd.DataFrame(
            {'COMPONENT 1': ['A', 'B'], 'COMPONENT 2': ['B', 'C'], 'LC_VALUE': [3, 4], 'COMMIT': ['abc', 'def']})

        # Test the alert function
        alert_data = alert(data_extracted, previous_data)

        self.assertEqual(len(alert_data), 2)


        self.assertEqual(alert_data.iloc[0]['NEW_LC_VALUE'], 4)
        self.assertEqual(alert_data.iloc[1]['NEW_LC_VALUE'], 6)

        self.assertEqual(alert_data.iloc[0]['OLD_LC_VALUE'], 1)
        self.assertEqual(alert_data.iloc[1]['OLD_LC_VALUE'], 2)

        self.assertTrue({"A", "B"}.issubset(set(alert_data['COMPONENT 1'].tolist())))
        self.assertTrue({"B", "C"}.issubset(set(alert_data['COMPONENT 2'].tolist())))

    def test_alert_messages_more_commits(self):
        # Create a dummy dataframe
        increasing_data = pd.DataFrame({
            'COMPONENT 1': ['A', 'C'],
            'COMPONENT 2': ['B', 'D'],
            'NEW_LC_VALUE': [7, 2],
            'OLD_LC_VALUE': [1, 1],
            'COMMIT': ['abc', 'abc']
        })

        # Test the alert_messages function
        message = alert_messages(increasing_data)

        self.assertEqual(message.count('Commit abc:'), 1)
        self.assertTrue(message.startswith('Commit abc:'))
        self.assertIn('Commit abc:', message)
        self.assertIn('ERROR', message)
        self.assertIn('A and B: NOW COUPLED', message)
        self.assertIn('(Value increased from 1 to 7)', message)

    def test_alert_messages_error(self):
        # Create a dummy dataframe
        increasing_data = pd.DataFrame({
            'COMPONENT 1': ['A'],
            'COMPONENT 2': ['B'],
            'NEW_LC_VALUE': [7],
            'OLD_LC_VALUE': [1],
            'COMMIT': ['abc']
        })

        # Test the alert_messages function
        message = alert_messages(increasing_data)

        self.assertEqual(message.count('Commit abc:'), 1)
        self.assertTrue(message.startswith('Commit abc:'))
        self.assertIn('Commit abc:', message)
        self.assertIn('ERROR', message)
        self.assertIn('A and B: NOW COUPLED', message)
        self.assertIn('(Value increased from 1 to 7)', message)

    def test_alert_messages_error_5(self):
        # Create a dummy dataframe
        increasing_data = pd.DataFrame({
            'COMPONENT 1': ['A'],
            'COMPONENT 2': ['B'],
            'NEW_LC_VALUE': [5],
            'OLD_LC_VALUE': [1],
            'COMMIT': ['abc']
        })

        # Test the alert_messages function
        message = alert_messages(increasing_data)

        self.assertEqual(message.count('Commit abc:'), 1)
        self.assertTrue(message.startswith('Commit abc:'))
        self.assertIn('Commit abc:', message)
        self.assertIn('ERROR', message)
        self.assertIn('A and B: NOW COUPLED', message)
        self.assertIn('(Value increased from 1 to 5)', message)

    def test_alert_messages_warning(self):
        # Create a dummy dataframe
        increasing_data = pd.DataFrame({
            'COMPONENT 1': ['B'],
            'COMPONENT 2': ['C'],
            'NEW_LC_VALUE': [4],
            'OLD_LC_VALUE': [2],
            'COMMIT': ['def']
        })

        # Test the alert_messages function
        message = alert_messages(increasing_data)

        self.assertIn('Commit def:', message)
        self.assertIn('WARNING', message)
        self.assertIn('B and C: IN COUPLING', message)
        self.assertIn('(Value increased from 2 to 4)', message)

    def test_alert_messages_info(self):
        # Create a dummy dataframe
        increasing_data = pd.DataFrame({
            'COMPONENT 1': ['B'],
            'COMPONENT 2': ['C'],
            'NEW_LC_VALUE': [7],
            'OLD_LC_VALUE': [5],
            'COMMIT': ['def']
        })

        # Test the alert_messages function
        message = alert_messages(increasing_data)

        self.assertIn('Commit def:', message)
        self.assertIn('INFO', message)
        self.assertIn('B and C: COUPLED', message)
        self.assertIn('(Value increased from 5 to 7)', message)

    def test_alert_messages_warning_new_coupling(self):
        # Create a dummy dataframe
        increasing_data = pd.DataFrame({
            'COMPONENT 1': ['B'],
            'COMPONENT 2': ['C'],
            'NEW_LC_VALUE': [1],
            'OLD_LC_VALUE': [0],
            'COMMIT': ['def']
        })

        # Test the alert_messages function
        message = alert_messages(increasing_data)

        self.assertIn('Commit def:', message)
        self.assertIn('WARNING', message)
        self.assertIn('B and C: NEW COUPLING', message)

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
        with patch('git.Repo.clone_from') as mock_clone:
            mock_clone.return_value = self.temp_dir
            with patch("coupling.util.checkout") as mock_checkout:
                mock_checkout.return_value = None
                with patch('pydriller.Repository') as mock_repository:
                    # Create a custom commit object for testing
                    commit_mock1 = Mock(hash='abc', modified_files=[MockFile('file1.txt'), MockFile('file2.py')])
                    commit_mock2 = Mock(hash='def', modified_files=[MockFile('file2.py'), MockFile('file3.py')])
                    mock_repository_instance = mock_repository.return_value
                    mock_repository_instance.traverse_commits.return_value = [commit_mock1, commit_mock2]

                    # Test the run function
                    exit_code, messages, _ = run('https://github.com/example/repo.git', 'main', 'abc')

                    self.assertEqual(exit_code, 1)
                    self.assertTrue("COUPLING" in messages)
                    self.assertTrue("WARNING" in messages)
                    self.assertTrue("NEW COUPLING" in messages)
                    self.assertTrue("abc" in messages)
                    self.assertTrue("def" in messages)

    def test_run_previous_commits_analyzed(self):
        # Mock the clone function
        with patch('git.Repo.clone_from') as mock_clone:
            mock_clone.return_value = self.temp_dir
            with patch("coupling.util.checkout") as mock_checkout:
                mock_checkout.return_value = None
                with patch('pydriller.Repository') as mock_repository:
                    # Create a custom commit object for testing
                    commit_mock1 = Mock(hash='abc', modified_files=[MockFile('file1.txt'), MockFile('file2.py')])
                    commit_mock2 = Mock(hash='def', modified_files=[MockFile('file2.py'), MockFile('file3.py')])
                    mock_repository_instance = mock_repository.return_value
                    mock_repository_instance.traverse_commits.return_value = [commit_mock1, commit_mock2]

                    # Test the run function
                    exit_code, messages, _ = run('https://github.com/example/repo.git', 'main', 'abc')

                    self.assertEqual(exit_code, 1)
                    self.assertTrue("COUPLING" in messages)
                    self.assertTrue("WARNING" in messages)
                    self.assertTrue("NEW COUPLING" in messages)
                    self.assertTrue("abc" in messages)
                    self.assertTrue("def" in messages)

    if __name__ == '__main__':
        unittest.main()

        # Add more assertions based on the expected behavior of the run function


# Helper class to mock PyDriller's ModifiedFile
class MockFile:
    def __init__(self, new_path):
        self.new_path = new_path


class MockFileNoNewPath:
    def __init__(self):
        self.new_path = None
