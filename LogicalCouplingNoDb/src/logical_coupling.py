import fnmatch
import itertools
import math
import os
import shutil
import traceback

import pandas
import pandas as pd
import pydriller

import util
from util import clone, checkout, initialize, root_calculator

logger = util.setup_logging('logical_coupling')


def load_previous_results(repo_name, path_to_repo, branch):
    file = f'.data/{repo_name}/LogicalCoupling.csv'
    file = os.path.relpath(file, os.getcwd())

    logger.info(f"Loading previous results from {file}")

    checkout(path_to_repo, branch, logger)

    ignore = f'{path_to_repo}/.lcignore'

    if os.path.exists(file):
        logger.info(f"Previous results found")
        data = pandas.read_csv(file)
        logger.debug(f"Previous results: {data}")
    else:
        logger.info(f"No previous results found")
        file = f'.data/{repo_name}'
        file = os.path.relpath(file, os.getcwd())
        os.makedirs(file, exist_ok=True)
        logger.info("Created directory for results: " + file)
        data = pandas.DataFrame(columns=['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE'])

    component_to_ignore = []
    logger.debug(f"Checking if ignore file exists: {ignore}")
    if os.path.exists(ignore):
        logger.info("Ignore file found")
        with open(ignore, 'r') as file:
            lines = file.readlines()

        component_to_ignore = [line.strip() for line in lines]
        component_to_ignore.append('.lcignore')
        logger.debug(f"Components to ignore: {component_to_ignore}")

    return data, component_to_ignore


def analyze_actual_commit(path_to_repo, branch, commit_hash, to_ignore):
    result = []
    logger.info(f"Analyzing commit {commit_hash} on branch {branch}")
    for commit in pydriller.Repository(path_to_repo, single=commit_hash, only_in_branch=branch).traverse_commits():

        modified_files = commit.modified_files

        for files in modified_files:
            logger.debug(f"Modified file: {files.new_path}")
            if not any(fnmatch.fnmatch(files.new_path, pattern) for pattern in to_ignore):
                result.append(files.new_path)
            else:
                logger.debug(f"Ignored file: {files.new_path}")

    # components = [root_calculator(file_path) for file_path in result]
    components = []
    for file_path in result:
        components.append(root_calculator(file_path))
    logger.debug(f"Components: {components}")

    components.sort()
    components = set(components)
    logger.debug(f"Components (string): {components}")
    components = [convertToNumber(component) for component in components]
    logger.debug(f"Components (number): {components}")
    combinations = list(itertools.combinations(components, 2))
    logger.debug(f"Combinations (unsorted): {combinations}")
    combinations_sorted = sorted(combinations)
    logger.debug(f"Combinations (sorted): {combinations_sorted}")
    component_1 = []
    component_2 = []
    lc_value = []
    for comb in combinations_sorted:
        component_1.append(convertFromNumber(comb[0]))
        component_2.append(convertFromNumber(comb[1]))
        lc_value.append(1)

    logger.info(f"Analyzed commit {commit_hash} on branch {branch}")
    return pandas.DataFrame({'COMPONENT 1': component_1, 'COMPONENT 2': component_2, 'LC_VALUE': lc_value})


def convertToNumber(s):
    return int.from_bytes(s.encode(), 'little')


def convertFromNumber(n):
    return n.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()


def update_data(data, new_data):
    # merged_df = pd.merge(data, new_data, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')
    # merged_df['LC_VALUE'] = merged_df['LC_VALUE_x'].fillna(0) + merged_df['LC_VALUE_y'].fillna(0)
    #
    # # Drop unnecessary columns
    # merged_df = merged_df[['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE']]

    merged_df = pd.merge(data, new_data, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')
    merged_df['LC_VALUE'] = merged_df['LC_VALUE_x'].fillna(0) + merged_df['LC_VALUE_y'].fillna(0)

    # Drop unnecessary columns
    merged_df = merged_df[['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE']]
    merged_df['LC_VALUE'] = merged_df['LC_VALUE'].astype(int)

    return merged_df


def alert(data_extracted, previous_data):
    new_rows = []
    # data = pd.DataFrame(columns=['COMPONENT 1', 'COMPONENT 2', 'NEW_LC_VALUE', 'OLD_LC_VALUE'])

    to_alert = previous_data[previous_data[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1).isin(
        data_extracted[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1))]

    new_coupling = data_extracted[~data_extracted[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1).isin(
        previous_data[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1))]
    new_coupling['LC_VALUE'] = 0

    to_alert['COMPONENT 1'] = to_alert['COMPONENT 1'].astype(str)
    to_alert['COMPONENT 2'] = to_alert['COMPONENT 2'].astype(str)
    new_coupling['COMPONENT 1'] = new_coupling['COMPONENT 1'].astype(str)
    new_coupling['COMPONENT 2'] = new_coupling['COMPONENT 2'].astype(str)
    to_alert = pd.merge(to_alert, new_coupling, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')

    to_alert['LC_VALUE'] = to_alert['LC_VALUE_x'].combine_first(to_alert['LC_VALUE_y'])
    to_alert = to_alert.drop(['LC_VALUE_x', 'LC_VALUE_y'], axis=1)

    for index, row in to_alert.iterrows():
        new_rows.append({'COMPONENT 1': row['COMPONENT 1'], 'COMPONENT 2': row['COMPONENT 2'],
                         'NEW_LC_VALUE': row['LC_VALUE'] + 1, 'OLD_LC_VALUE': row['LC_VALUE']})
    return pd.DataFrame(new_rows)


def alert_messages(increasing_data):
    message = ""
    for index, row in increasing_data.iterrows():
        if row['OLD_LC_VALUE'] >= 5:
            message += f"The new coupling between the coupled components {row['COMPONENT 1']} and {row['COMPONENT 2']} is increased: {row['NEW_LC_VALUE']}\n"
        elif row['NEW_LC_VALUE'] >= 5:
            message += f"The components  {row['COMPONENT 1']} and {row['COMPONENT 2']} are coupled: {row['NEW_LC_VALUE']}\n"
        else:
            message += f" Logical coupling between {row['COMPONENT 1']} and {row['COMPONENT 2']} increased from {row['OLD_LC_VALUE']} to {row['NEW_LC_VALUE']}\n"
    return message


def save(data, repo_name):
    file = f'.data/{repo_name}/LogicalCoupling.csv'
    file = os.path.relpath(file, os.getcwd())
    data.to_csv(file, index=False)


def run(repo_url, branch, commit_hash):
    global logger
    logger = util.setup_logging('logical_coupling')

    try:
        exit_code = 0
        logger.info("Logical coupling tool started")
        initialized_data_path = initialize()
        logger.debug(f"Initialized: {initialized_data_path}, absolute path: {os.path.abspath(initialized_data_path)}")

        commit_hash = commit_hash
        branch = branch
        repo_url = repo_url
        repo_name = repo_url.split('/')[-1].split('.')[0] + "b:" + branch
        logger.debug(f"Repo name: {repo_name}")

        path_to_cloned_repo = clone(repo_url)

        logger.info(f"Cloned repo: {path_to_cloned_repo}")

        logger.info(f"Loading previous results")

        data, components_to_ignore = load_previous_results(repo_name, path_to_cloned_repo, branch)

        logger.info(f"Loaded previous results")
        logger.debug(f"Data: {data}")
        logger.debug(f"Components to ignore: {components_to_ignore}")

        new_data = analyze_actual_commit(path_to_cloned_repo, branch, commit_hash, components_to_ignore)

        if new_data.empty:
            logger.info("No new coupling found ")
        else:
            logger.info("New coupling found ")
            exit_code = 1

        save(new_data, repo_name)
        alert_data = alert(new_data, data)
        logger.debug(f"Alert data: {alert_data}")
        messages = alert_messages(alert_data)
        logger.debug(f"Messages: {messages}")
        logger.info("Logical coupling tool finished")
        return exit_code, messages

    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logger.info("Logical coupling tool finished with error")
        return -1, "Error in logical coupling tool"

    finally:
        logger.debug("Deleting temporary files")
        shutil.rmtree('.temp/', ignore_errors=True)
