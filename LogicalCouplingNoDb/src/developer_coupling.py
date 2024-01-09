import argparse
import fnmatch
import itertools
import math
import os
import sys
from operator import itemgetter

import pandas
import pandas as pd
import pydriller
from git import Repo


def checkout(repo_url):
    path = f".temp/{repo_url.replace('/', '_')}"
    Repo.clone_from(repo_url, path)
    return path


def load_previous_results(path_to_data, path_to_dev_ignore_file, path_to_comp_ignore_file):
    result = []

    if os.path.exists(path_to_data):
        print("Previous results found")
        result = os.listdir(data)

    else:
        print("No previous results found")

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

    for component in components:
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


def root_calculator(file_path: str) -> str:
    path = file_path.lstrip(os.sep)
    root = path[:path.index(os.sep)] if os.sep in path else path
    return root


def print_alert(data):
    for index, row in data.iterrows():
        print(f"Developer {row['DEVELOPER']} modified component {row['COMPONENT']} for the first time")


def initialize():
    if not os.path.exists('../.data'):
        os.mkdir('../.data')


if __name__ == '__main__':
    exit_code = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit_hash")
    parser.add_argument("--branch")
    parser.add_argument("--repo_url")

    args = parser.parse_args()
    print(args.repo_url, args.branch, args.commit_hash)

    initialize()

    commit_hash = args.commit_hash
    branch = args.branch
    repo_url = args.repo_url
    repo_name = repo_url.split('/')[-1].split('.')[0] + "b:" + branch

    path_to_data = f'../.data/{repo_name}/developer_coupling'
    path_to_dev_ignore_file = f'../.data/{repo_name}/.devignore'
    path_to_comp_ignore_file = f'../.data/{repo_name}/.dev_comp_ignore'

    path_to_cloned_repo = checkout(repo_url)
    data, components_to_ignore, developers_to_ignore = load_previous_results(path_to_data,
                                                                             path_to_dev_ignore_file,
                                                                             path_to_comp_ignore_file)
    new_data = analyze_and_save_actual_commit(path_to_cloned_repo, branch, commit_hash, components_to_ignore,
                                              developers_to_ignore)

    if new_data.empty:
        print("No new coupling found ")
    else:
        exit_code = 1

    print_alert(new_data)
    sys.exit(exit_code)
