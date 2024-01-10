import os
import shutil
import unittest
from git import Repo


from LogicalCouplingNoDb.src.logical_coupling import analyze_actual_commit, load_previous_results


class TestLoader(unittest.TestCase):
    # Replace these values with your Neo4j database credentials and URI
    path = ".ProjectToTestLogicalCouplingTool"

    def test_load_lc_ignore_on_different_branches(self):

        # rorepo is a Repo instance pointing to the git-python repository.
        # For all you know, the first argument to Repo is a path to the repository
        # you want to work with
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
        git.clone(b="my_new_branch")  # create a new branch
        # git.branch("my_new_branch")  # pass strings for full control over argument order
        git.for_each_ref()  # '-' becomes '_' when calling it


        lcignore = ".lcignore"

        with open(f"{self.path}/{lcignore}", "w") as f:
            f.write("component1/*")

        add_file = [lcignore]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Updated lcignore")

        git.clone('main')

        _, component_to_ignore = load_previous_results("ProjectToTestLogicalCouplingTool", self.path, "my_new_branch")
        expected = ["component1/*"]
        self.assertTrue(component_to_ignore==expected, "Load failed.")

        _, component_to_ignore = load_previous_results("ProjectToTestLogicalCouplingTool", self.path,
                                                          "main")
        expected = []
        self.assertTrue(component_to_ignore == expected, "Load failed.")

    def tearDown(self):
        shutil.rmtree(self.path)

    if __name__ == '__main__':
        unittest.main()