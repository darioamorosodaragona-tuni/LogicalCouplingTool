import argparse
import fnmatch
import itertools
import math
import os
import shutil
import sys
import traceback
from operator import itemgetter

import pandas
import pandas as pd
import pydriller
from git import Repo

from util import clone, checkout, initialize, root_calculator


def load_previous_results(path_to_data, path_to_repo, branch, path_to_dev_ignore_file, path_to_comp_ignore_file):
    result = []

    if os.path.exists(path_to_data):
        print("Previous results found")
        result = os.listdir(path_to_data)
        # print(path_to_data)
        # print(os.path.abspath(path_to_data))
        # print(os.path.relpath('LogicalCouplingNoDb', f'{os.getcwd()}'))

    else:
        print("No previous results found")
        os.makedirs(path_to_data, exist_ok=True)
        # print("LOADED PREVIOUS RESULTS")
        # print(path_to_data)
        # print(os.path.abspath(path_to_data))

    checkout(path_to_repo, branch)

    component_to_ignore = []
    developer_to_ignore = []
    if os.path.exists(path_to_comp_ignore_file):
        with open(path_to_comp_ignore_file, 'r') as file:
            lines = file.readlines()

        component_to_ignore = [line.strip() for line in lines]

    if os.path.exists(path_to_dev_ignore_file):
        with open(path_to_dev_ignore_file, 'r') as file:
            lines = file.readlines()

        developer_to_ignore = [line.strip() for line in lines]

    return result, component_to_ignore, developer_to_ignore


def analyze_and_save_actual_commit(path_to_repo, branch, commit_hash, components_to_ignore, devs_to_ignore, data,
                                   path_to_data):
    roots = []
    developer = ""
    for commit in pydriller.Repository(path_to_repo, single=commit_hash, only_in_branch=branch).traverse_commits():

        if commit.author.email in devs_to_ignore:
            return pandas.DataFrame(
                {'COMPONENT': [], 'DEVELOPER': []})

        modified_files = commit.modified_files

        for files in modified_files:
            if not any(fnmatch.fnmatch(files.new_path, pattern) for pattern in components_to_ignore):
                roots.append(files.new_path)
                developer = commit.author.email

    # components = [root_calculator(file_path) for file_path in result]
    components = []
    for file_path in roots:
        components.append(root_calculator(file_path))

    components_to_alert = []

    print(data)
    for component in components:
        print(component)
        if component in data:
            with open(f"{path_to_data}/{component}", 'r') as file:
                lines = file.readlines()
            developers = [line.strip() for line in lines]

            if developer not in developers:
                components_to_alert.append(component)

                with open(f"{path_to_data}/{component}", 'a') as file:
                    file.write(developer)
        else:
            with open(f"{path_to_data}/{component}", 'w+') as file:
                file.write(developer)

    return pandas.DataFrame({'COMPONENT': components_to_alert, 'DEVELOPER': [developer] * len(components_to_alert)})


def alert_message(data):
    messages = ""
    for index, row in data.iterrows():
        messages += f"Developer {row['DEVELOPER']} modified component {row['COMPONENT']} for the first time\n"
    return messages


def run(repo_url, branch, commit_hash):
    try:
        exit_code = 0

        initialize()

        commit_hash = commit_hash
        branch = branch
        repo_url = repo_url
        repo_name = repo_url.split('/')[-1].split('.')[0] + "b:" + branch

        path_to_data = f'.data/{repo_name}/developer_coupling'
        path_to_data = os.path.relpath(path_to_data, f'{os.getcwd()}')

        path_to_cloned_repo = clone(repo_url)

        path_to_dev_ignore_file = f'{path_to_cloned_repo}/.devignore'
        path_to_comp_ignore_file = f'{path_to_cloned_repo}/.dev_comp_ignore'

        data, components_to_ignore, developers_to_ignore = load_previous_results(path_to_data,
                                                                                 path_to_cloned_repo,
                                                                                 branch,
                                                                                 path_to_dev_ignore_file,
                                                                                 path_to_comp_ignore_file)

        new_data = analyze_and_save_actual_commit(path_to_cloned_repo, branch, commit_hash, components_to_ignore,
                                                  developers_to_ignore, data, path_to_data)
        message = alert_message(new_data)

        if not new_data.empty:
            exit_code = 1, message

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        exit_code = -1
        message = "Error in developer coupling tool"

    finally:
        shutil.rmtree('.temp/', ignore_errors=True)

    return exit_code, message
