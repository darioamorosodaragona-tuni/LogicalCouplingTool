import os
import shutil
import unittest
import pandas as pd
from neo4j import GraphDatabase
from neomodel import db
from git import Repo

# import src.DBManager as DBManager
from  coupling.logical_coupling import update_data, alert, save, load_previous_results, \
    analyze_commits

@unittest.skip("obsolete tests")

class TestCalculator(unittest.TestCase):
    # Replace these values with your Neo4j database credentials and URI
    path = ".ProjectToTestLogicalCouplingTool"
    __test__ = False


    def test_analyze_actual_commit(self):

        # rorepo is a Repo instance pointing to the git-python repository.
        # For all you know, the first argument to Repo is a path to the repository
        # you want to work with
        os.makedirs(self.path, exist_ok=True)
        repo = Repo.init(self.path)
        # repo = Repo(self.path)

        update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component1'):
            os.makedirs(f'{self.path}/component1')

        with open(f"{self.path}/{update_file_1}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_2 = "component2/B.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component2'):
            os.makedirs(f'{self.path}/component2')

        with open(f"{self.path}/{update_file_2}", "a") as f:
            f.write("\nUpdate version 2")

        add_file = [update_file_1, update_file_2]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Update to file2")

        result = analyze_commits(self.path, 'main', 'HEAD', [])
        expected = {'COMPONENT 1': ['component1'], 'COMPONENT 2': ['component2'], 'LC_VALUE': [1]}
        df_expected = pd.DataFrame(expected)
        self.assertTrue(df_expected.equals(result), "Analyze actual commit failed.")
        shutil.rmtree(self.path)



    def test_analyze_actual_commit_inverse_order(self):

            # rorepo is a Repo instance pointing to the git-python repository.
            # For all you know, the first argument to Repo is a path to the repository
            # you want to work with
            os.makedirs(self.path, exist_ok=True)
            repo = Repo.init(self.path)
            # repo = Repo(self.path)



            update_file_2 = "component2/B.py"  # we'll use local_dir/dir1/file2.txt
            if not os.path.exists(f'{self.path}/component2'):
                os.makedirs(f'{self.path}/component2')

            with open(f"{self.path}/{update_file_2}", "a") as f:
                f.write("\nUpdate version 2")

            update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
            if not os.path.exists(f'{self.path}/component1'):
                os.makedirs(f'{self.path}/component1')

            with open(f"{self.path}/{update_file_1}", "a") as f:
                f.write("\nUpdate version 2")

            add_file = [update_file_2, update_file_1]  # relative path from git root
            repo.index.add(add_file)
            repo.index.commit("Update to file2")

            result = analyze_commits(self.path, 'main', 'HEAD', [])
            expected = {'COMPONENT 1': ['component1'], 'COMPONENT 2': ['component2'], 'LC_VALUE': [1]}
            df_expected = pd.DataFrame(expected)
            self.assertTrue(df_expected.equals(result), "Analyze actual commit failed.")
            shutil.rmtree(self.path)


    def test_analyze_actual_commit_ignore_whole_component(self):

        # rorepo is a Repo instance pointing to the git-python repository.
        # For all you know, the first argument to Repo is a path to the repository
        # you want to work with
        os.makedirs(self.path, exist_ok=True)
        repo = Repo.init(self.path)
        # repo = Repo(self.path)

        update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component1'):
            os.makedirs(f'{self.path}/component1')

        with open(f"{self.path}/{update_file_1}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_2 = "component2/B.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component2'):
            os.makedirs(f'{self.path}/component2')

        with open(f"{self.path}/{update_file_2}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_3 = "component3/B.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component3'):
            os.makedirs(f'{self.path}/component3')

        with open(f"{self.path}/{update_file_3}", "a") as f:
            f.write("\nUpdate version 2")

        add_file = [update_file_1, update_file_2, update_file_3]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Update to file2")
        ignore = ['component3/*']

        result = analyze_commits(self.path, 'main', 'HEAD', ignore)
        expected = {'COMPONENT 1': ['component1'], 'COMPONENT 2': ['component2'], 'LC_VALUE': [1]}
        df_expected = pd.DataFrame(expected)
        self.assertTrue(df_expected.equals(result), "Analyze actual commit failed.")
        shutil.rmtree(self.path)

    def test_analyze_actual_commit_ignore_file(self):

        # rorepo is a Repo instance pointing to the git-python repository.
        # For all you know, the first argument to Repo is a path to the repository
        # you want to work with
        os.makedirs(self.path, exist_ok=True)
        repo = Repo.init(self.path)
        # repo = Repo(self.path)

        update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component1'):
            os.makedirs(f'{self.path}/component1')

        with open(f"{self.path}/{update_file_1}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_2 = "component2/B.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component2'):
            os.makedirs(f'{self.path}/component2')

        with open(f"{self.path}/{update_file_2}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_3 = "component3/B.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component3'):
            os.makedirs(f'{self.path}/component3')

        with open(f"{self.path}/{update_file_3}", "a") as f:
            f.write("\nUpdate version 2")

        add_file = [update_file_1, update_file_2, update_file_3]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Update to file2")
        ignore = ['component3/B.py']

        result = analyze_commits(self.path, 'main', 'HEAD', ignore)
        expected = {'COMPONENT 1': ['component1'], 'COMPONENT 2': ['component2'], 'LC_VALUE': [1]}
        df_expected = pd.DataFrame(expected)
        self.assertTrue(df_expected.equals(result), "Analyze actual commit failed.")
        shutil.rmtree(self.path)

    def test_analyze_actual_commit_ignore_one_on_two_file(self):

            # rorepo is a Repo instance pointing to the git-python repository.
            # For all you know, the first argument to Repo is a path to the repository
            # you want to work with
            os.makedirs(self.path, exist_ok=True)
            repo = Repo.init(self.path)
            # repo = Repo(self.path)

            update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
            if not os.path.exists(f'{self.path}/component1'):
                os.makedirs(f'{self.path}/component1')

            with open(f"{self.path}/{update_file_1}", "a") as f:
                f.write("\nUpdate version 2")

            update_file_2 = "component2/B.py"  # we'll use local_dir/dir1/file2.txt
            if not os.path.exists(f'{self.path}/component2'):
                os.makedirs(f'{self.path}/component2')

            with open(f"{self.path}/{update_file_2}", "a") as f:
                f.write("\nUpdate version 2")


            add_file = [update_file_1, update_file_2]  # relative path from git root
            repo.index.add(add_file)
            repo.index.commit("Update to file2")
            ignore = ['component2/*']

            result = analyze_commits(self.path, 'main', 'HEAD', ignore)
            expected = {'COMPONENT 1': [], 'COMPONENT 2': [], 'LC_VALUE': []}
            df_expected = pd.DataFrame(expected)
            self.assertTrue(df_expected.equals(result), "Analyze actual commit failed.")

    def test_analyze_actual_commit_ignore_intermediate_path(self):

        # rorepo is a Repo instance pointing to the git-python repository.
        # For all you know, the first argument to Repo is a path to the repository
        # you want to work with
        os.makedirs(self.path, exist_ok=True)
        repo = Repo.init(self.path)
        # repo = Repo(self.path)

        update_file_1 = "component1/A.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component1'):
            os.makedirs(f'{self.path}/component1')

        with open(f"{self.path}/{update_file_1}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_2 = "component2/B.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component2'):
            os.makedirs(f'{self.path}/component2')

        with open(f"{self.path}/{update_file_2}", "a") as f:
            f.write("\nUpdate version 2")

        update_file_3 = "component2/dir/G.py"  # we'll use local_dir/dir1/file2.txt
        if not os.path.exists(f'{self.path}/component2/dir'):
            os.makedirs(f'{self.path}/component2/dir')

        with open(f"{self.path}/{update_file_3}", "a") as f:
            f.write("\nUpdate version 2")

        add_file = [update_file_1, update_file_2, update_file_3]  # relative path from git root
        repo.index.add(add_file)
        repo.index.commit("Update to file2")
        ignore = ['component2/dir/*']

        result = analyze_commits(self.path, 'main', 'HEAD', ignore)
        expected = {'COMPONENT 1': ['component1'], 'COMPONENT 2': ['component2'], 'LC_VALUE': [1]}
        df_expected = pd.DataFrame(expected)
        self.assertTrue(df_expected.equals(result), "Analyze actual commit failed.")

    def tearDown(self):
        shutil.rmtree(self.path, ignore_errors=True)



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
