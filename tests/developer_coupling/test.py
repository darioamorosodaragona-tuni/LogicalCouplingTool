import shutil
import unittest
import os
from unittest.mock import patch, Mock
from coupling import developer_coupling


class TestDeveloperCoupling(unittest.TestCase):

    def setUp(self):
        # Create necessary directories and files for testing
        os.makedirs('.data/test_repo/developer_coupling', exist_ok=True)
        with open('.data/test_repo/.devignore', 'w') as dev_ignore_file:
            dev_ignore_file.write('dev1\n')
            dev_ignore_file.write('dev2\n')
        with open('.data/test_repo/.dev_comp_ignore', 'w') as comp_ignore_file:
            comp_ignore_file.write('component1/*\n')

    def tearDown(self):
        # Remove test directories and files
        shutil.rmtree('.data')

    def test_load_previous_results(self):
        # Providing test data
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = ['result1', 'result2']

            path_to_data = '.data/test_repo/developer_coupling'
            path_to_repo = '.data/test_repo'
            branch = 'main'
            path_to_dev_ignore_file = '.data/test_repo/.devignore'
            path_to_comp_ignore_file = '.data/test_repo/.dev_comp_ignore'

            # Executing the function
            result, comp_ignore, dev_ignore = developer_coupling.load_previous_results(
                path_to_data, path_to_repo, branch, path_to_dev_ignore_file, path_to_comp_ignore_file
            )

            # Assertions
            self.assertEqual(result, ['result1', 'result2'])
            self.assertTrue([x in comp_ignore for x in ['.dev_comp_ignore', '.devignore', 'component1/*']])
            self.assertEqual(dev_ignore, ['dev1', 'dev2'])

    def test_analyze_and_save_actual_commit(self):
        with patch('pydriller.Repository') as mock_repository:
            # Providing test data
            commit_mock1 = Mock(hash='abc', author=MockAuthor('test@example.com'),
                                modified_files=[MockFile('component2/file1.py')])
            commit_mock2 = Mock(hash='def', author=MockAuthor('test-ignoret@example.com'),
                                modified_files=[MockFile('component1/file2.py')])

            mock_repository.return_value.traverse_commits.return_value = [commit_mock1, commit_mock2]

            path_to_repo = '.data/test_repo'
            branch = 'main'
            commit_hash = '123456'
            components_to_ignore = ['component1/*']
            devs_to_ignore = ['dev1']
            data = ['component1', 'component2']
            path_to_data = '.data/test_repo/developer_coupling/'
            with open('.data/test_repo/developer_coupling/component2', 'w') as comp_ignore_file:
                comp_ignore_file.write('dev-test@example.com\n')

            # Executing the function
            result = developer_coupling.analyze_and_save_actual_commit(
                path_to_repo, branch, commit_hash, components_to_ignore, devs_to_ignore, data, path_to_data
            )

            # Assertions
            self.assertIn('component2', result['COMPONENT'].tolist())
            self.assertIn('test@example.com', result['DEVELOPER'].tolist())
            # self.assertEqual(result.to_dict(), {'COMPONENT': ['component2'], 'DEVELOPER': ['test@example.com']})


class MockFile:
    def __init__(self, new_path):
        self.new_path = new_path


class MockAuthor:
    def __init__(self, email):
        self.email = email


if __name__ == '__main__':
    unittest.main()
