import os
import shutil
import unittest
from unittest.mock import patch, MagicMock

from git import Repo

import coupling.util
from coupling.logical_coupling import analyze_commits, load_previous_results


class TestLoader(unittest.TestCase):
    # Replace these values with your Neo4j database credentials and URI
    path = ".ProjectToTestLogicalCouplingTool"

    def test_load_lc_ignore_on_different_branches(self):
        # rorepo is a Repo instance pointing to the git-python repository.
        # For all you know, the first argument to Repo is a path to the repository
        # you want to work with
        print(os.curdir)
        os.makedirs(self.path, exist_ok=True)
        repo = Repo.init(self.path)
        # repo = Repo(self.path)

        update_file_3 = "A.py"  # we'll use local_dir/dir1/file2.txt
        with open(f"{self.path}/{update_file_3}", "a") as f:
            f.write("\nUpdate version 2")

        add_file = [update_file_3]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Update to file2")

        git = repo.git
        git.checkout(b="my_new_branch")  # create a new branch
        # git.branch("my_new_branch")  # pass strings for full control over argument order
        git.for_each_ref()  # '-' becomes '_' when calling it

        lcignore = ".lcignore"

        with open(f"{self.path}/{lcignore}", "w") as f:
            f.write("component1/*")

        add_file = [lcignore]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Updated lcignore")

        git.checkout('main')

        with patch('coupling.util.logging') as mock_logger:
            mock_info = MagicMock()
            mock_logger.info = mock_info
            coupling.util.checkout(self.path, 'my_new_branch', mock_logger)

        _, component_to_ignore, _ = load_previous_results("ProjectToTestLogicalCouplingTool", self.path)
        expected = ["component1/*", lcignore]

        self.assertTrue(component_to_ignore == expected, "Load failed.")

        with patch('coupling.util.logging') as mock_logger:
            mock_info = MagicMock()
            mock_logger.info = mock_info
            coupling.util.checkout(self.path, 'main', mock_logger)

        _, component_to_ignore, _ = load_previous_results("ProjectToTestLogicalCouplingTool", self.path)
        expected = []
        self.assertTrue(component_to_ignore == expected, "Load failed.")

    def tearDown(self):
        shutil.rmtree(self.path)

    if __name__ == '__main__':
        unittest.main()
