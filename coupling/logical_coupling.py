import fnmatch
import itertools
import math
import os
import shutil
import traceback

import git
import pandas
import pandas as pd
import pydriller
import tqdm

# from .util import *
from coupling import util

logger = util.setup_logging('logical_coupling')


def load_previous_results(repo_name, path_to_repo):
    """
    Load previous logical coupling results from CSV files.

    Parameters:
    - repo_name (str): Name of the repository.
    - path_to_repo (str): Path to the local repository.
    - branch (str): Branch name.

    Returns:
    - data (pd.DataFrame): DataFrame containing previous logical coupling data.
    - component_to_ignore (list): List of components to ignore.
    - commits_analyzed_dataframe (pd.DataFrame): DataFrame containing previously analyzed commits.
    """

    commits_analyzed = f'.data/{repo_name}/analyzed.csv'
    file = f'.data/{repo_name}/LogicalCoupling.csv'
    file = os.path.relpath(file, os.getcwd())

    logger.info(f"Loading previous results from {file}")

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
        logger.info("Created directory for results: " + os.path.abspath(file))
        data = pandas.DataFrame(columns=['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE'])

    if os.path.exists(commits_analyzed):
        logger.info(f"Previous commits analyzed found")
        commits_analyzed_dataframe = pandas.read_csv(commits_analyzed)
        logger.debug(f"Previous results: {commits_analyzed_dataframe}")
    else:
        logger.info(f"No previous commits found")
        file = f'.data/{repo_name}'
        file = os.path.relpath(file, os.getcwd())
        os.makedirs(file, exist_ok=True)
        logger.info("Created directory for results: " + file)
        commits_analyzed_dataframe = pandas.DataFrame(columns=['COMMITS ANALYZED'])
        commits_analyzed_dataframe.to_csv(commits_analyzed, index=False)

    component_to_ignore = []
    logger.debug(f"Checking if ignore file exists: {ignore}")
    if os.path.exists(ignore):
        logger.info("Ignore file found")
        with open(ignore, 'r') as file:
            lines = file.readlines()

        component_to_ignore = [line.strip() for line in lines]
        component_to_ignore.append('.lcignore')
        logger.debug(f"Components to ignore: {component_to_ignore}")

    logger.debug(f"Commits analyzed: {commits_analyzed_dataframe}")

    return data, component_to_ignore, commits_analyzed_dataframe


def analyze_commits(path_to_repo, branch, commits, last_commit_analyzed, to_ignore):
    """
        Analyze commits for logical coupling.

        Parameters:
        - path_to_repo (str): Path to the local repository.
        - branch (str): Branch name.
        - commits (list): List of commit hashes to analyze.
        - last_commit_analyzed (str): Last commit already analyzed.
        - to_ignore (list): List of components to ignore.

        Returns:
        - grouped_df (pd.DataFrame): Grouped DataFrame with logical coupling results.
        - commits_analyzed (list): List of commits analyzed during the process.
        """
    rows = []
    commits_analyzed = []

    logger.info(f"Analyzing commits {commits} on branch {branch}")

    if last_commit_analyzed is None:

        logger.info("No previous commits analyzed")
        logger.debug(f"Analyzing commits {commits} on branch {branch}")
        repository = pydriller.Repository(path_to_repo, to_commit=commits[-1],
                                          only_in_branch=branch)

    else:
        if last_commit_analyzed in commits:
            logger.debug(f"Last commit analyzed {last_commit_analyzed} is in commits {commits}")
            commits.remove(last_commit_analyzed)
            # commits = commits[commits.index(last_commit_analyzed) + 1:]
            logger.debug(f"Commits to analyze: {commits}")

        repo = git.Repo(path_to_repo)
        logger.info(f"Previous commits analyzed: {last_commit_analyzed}")
        logger.debug(f"Analyzing commits {commits} on branch {branch}")
        commits_to_analyze = repo.git.execute(['git', 'rev-list', '--ancestry-path',
                                               '%s..%s' % (last_commit_analyzed, commits[0])]).split()
        logger.debug(f"Commits to analyze: {commits_to_analyze}")
        logger.info(f"Analyzing {len(commits_to_analyze)} commits on branch {branch}")
        repository = pydriller.Repository(path_to_repo, only_commits=commits_to_analyze,
                                          only_in_branch=branch)

    total_modified_files = 0
    for commit in tqdm.tqdm(repository.traverse_commits(), desc="Analyzing commits", unit="commit", position=0,
                            leave=True):
        result = []

        # if commit.hash == last_commit_analyzed:
        #     logger.debug(f"Commit {commit.hash} already analyzed")
        #     continue

        modified_files = commit.modified_files
        total_modified_files += len(modified_files)

        for files in tqdm.tqdm(modified_files, desc="Analyzing files", unit="file", position=1, leave=False):
            logger.debug(f"Modified file: {files.new_path}")
            if files.new_path is None:
                continue
            if not any(fnmatch.fnmatch(files.new_path, pattern) for pattern in to_ignore):
                result.append(files.new_path)
            else:
                logger.debug(f"Ignored file: {files.new_path}")

        # components = [root_calculator(file_path) for file_path in result]
        components = []
        for file_path in result:
            components.append(util.root_calculator(file_path))
        logger.debug(f"Components: {components}")

        components.sort()
        components = set(components)
        logger.debug(f"Components (string): {components}")
        components = [convertToNumber(component) for component in components]
        logger.debug(f"Components (number): {components}")
        combinations = list(itertools.combinations(components, 2))
        logger.debug(f"Combinations (unsorted): {combinations}")
        combinations_sorted = [tuple(sorted(comb)) for comb in combinations]
        logger.debug(f"Combinations (sorted): {combinations_sorted}")

        for comb in combinations_sorted:
            rows.append(
                {'COMPONENT 1': convertFromNumber(comb[0]), 'COMPONENT 2': convertFromNumber(comb[1]), 'LC_VALUE': 1,
                 'COMMIT': commit.hash})

        logger.info(f"Analyzed commit {commit.hash} on branch {branch}")

        if not combinations_sorted:
            logger.debug("No new coupling found in commit " + commit.hash)

        commits_analyzed.append(commit.hash)

    logger.info(f"Analyzed {total_modified_files} modified files on branch {branch}")

    result = pd.DataFrame(rows)

    if result.empty:
        logger.info("No new coupling found")
        return result, commits_analyzed

    grouped_df = result.groupby(['COMPONENT 1', 'COMPONENT 2']).agg({
        'LC_VALUE': 'sum',
        'COMMIT': lambda x: list(x)
    }).reset_index()

    # Rename the 'LC_VALUE' column to the original name
    # grouped_df = grouped_df.rename(columns={'LC_VALUE': 'LC_VALUE'})
    return grouped_df, commits_analyzed


def convertToNumber(s):
    """
       Convert a string to a unique numeric value.

       Parameters:
       - s (str): Input string.

       Returns:
       - int: Numeric representation of the input string.
       """
    return int.from_bytes(s.encode(), 'little')


def convertFromNumber(n):
    """
       Convert a numeric value back to its original string representation.

       Parameters:
       - n (int): Numeric value.

       Returns:
       - str: Original string representation.
       """
    return n.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()


def update_data(data, new_data):
    """
        Update the logical coupling data with new analysis results.

        Parameters:
        - data (pd.DataFrame): Existing logical coupling data.
        - new_data (pd.DataFrame): New logical coupling data to be merged.

        Returns:
        - merged_df (pd.DataFrame): Merged DataFrame containing updated logical coupling data.
        """

    merged_df = pd.merge(data, new_data, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')
    merged_df['LC_VALUE'] = merged_df['LC_VALUE_x'].fillna(0) + merged_df['LC_VALUE_y'].fillna(0)

    # Drop unnecessary columns
    merged_df = merged_df[['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE']]
    merged_df['LC_VALUE'] = merged_df['LC_VALUE'].astype(int)

    return merged_df


def alert(data_extracted, previous_data):
    """
       Identify and alert about changes in logical coupling.

       Parameters:
       - data_extracted (pd.DataFrame): Newly extracted logical coupling data.
       - previous_data (pd.DataFrame): Previous logical coupling data.

       Returns:
       - alert_df (pd.DataFrame): DataFrame containing alert information.
       """
    new_rows = []
    to_alert = pd.merge(previous_data, data_extracted[['COMPONENT 1', 'COMPONENT 2', 'COMMIT', 'LC_VALUE']],
                        on=['COMPONENT 1', 'COMPONENT 2'], how='inner')

    to_alert["LC_VALUE_NEW"] = to_alert["LC_VALUE_y"]
    to_alert["LC_VALUE_OLD"] = to_alert["LC_VALUE_x"]
    to_alert = to_alert.drop(['LC_VALUE_x', 'LC_VALUE_y'], axis=1)

    logger.debug(f"Previous data: {previous_data}")
    logger.debug(f"Data extracted: {data_extracted}")
    logger.debug(f"To alert: {to_alert}")

    new_coupling = data_extracted[~data_extracted[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1).isin(
        previous_data[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1))]
    new_coupling['LC_VALUE_OLD'] = 0
    new_coupling['LC_VALUE_NEW'] = 1

    logger.debug(f"New coupling: {new_coupling}")

    to_alert['COMPONENT 1'] = to_alert['COMPONENT 1'].astype(str)
    to_alert['COMPONENT 2'] = to_alert['COMPONENT 2'].astype(str)
    new_coupling['COMPONENT 1'] = new_coupling['COMPONENT 1'].astype(str)
    new_coupling['COMPONENT 2'] = new_coupling['COMPONENT 2'].astype(str)
    to_alert = pd.merge(to_alert, new_coupling, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')

    to_alert['LC_VALUE_OLD'] = to_alert['LC_VALUE_OLD_x'].combine_first(to_alert['LC_VALUE_OLD_y'])
    to_alert['LC_VALUE_NEW'] = to_alert['LC_VALUE_NEW_x'].combine_first(to_alert['LC_VALUE_NEW_y'])
    to_alert['COMMIT'] = to_alert['COMMIT_x'].combine_first(to_alert['COMMIT_y'])

    to_alert = to_alert.drop(
        ['LC_VALUE_NEW_x', 'LC_VALUE_NEW_y', 'LC_VALUE_OLD_x', 'LC_VALUE_OLD_y', 'COMMIT_x', 'COMMIT_y', 'LC_VALUE'],
        axis=1)

    logger.debug(f"To alert: {to_alert}")

    for index, row in to_alert.iterrows():
        new_rows.append({'COMPONENT 1': row['COMPONENT 1'], 'COMPONENT 2': row['COMPONENT 2'],
                         'NEW_LC_VALUE': row['LC_VALUE_NEW'] + row['LC_VALUE_OLD'], 'OLD_LC_VALUE': row['LC_VALUE_OLD'],
                         'COMMIT': row['COMMIT']})

    logger.debug(f"New rows: {new_rows}")
    logger.debug(f"New rows (dataframe): {pd.DataFrame(new_rows)}")
    return pd.DataFrame(new_rows)


def alert_messages(increasing_data):
    """
       Generate alert messages based on changes in logical coupling.

       Parameters:
       - increasing_data (pd.DataFrame): DataFrame containing increased logical coupling information.

       Returns:
       - str: Generated alert messages.
       """
    message = ""
    commit = ""
    for index, row in increasing_data.iterrows():
        if commit != row['COMMIT']:
            commit = row['COMMIT']
            message += f"Commit {commit}:\n"

        if row['OLD_LC_VALUE'] >= 5:
            message += f"INFO: {row['COMPONENT 1']} and {row['COMPONENT 2']}: COUPLED. (Value increased from {row['OLD_LC_VALUE']} to {row['NEW_LC_VALUE']})\n)"
        elif row['NEW_LC_VALUE'] >= 5:
            message += f"ERROR: {row['COMPONENT 1']} and {row['COMPONENT 2']}: NOW COUPLED. (Value increased from {row['OLD_LC_VALUE']} to {row['NEW_LC_VALUE']})\n"
        elif row['NEW_LC_VALUE'] == 1:
            message += f"WARNING: {row['COMPONENT 1']} and {row['COMPONENT 2']}: NEW COUPLING\n"
        else:
            message += f"WARNING:  {row['COMPONENT 1']} and {row['COMPONENT 2']}: IN COUPLING. (Value increased from {row['OLD_LC_VALUE']} to {row['NEW_LC_VALUE']})\n"
    return message


def save(data, repo_name, new_commits_analyzed, commits_analyzed):
    """
       Save logical coupling data and analyzed commits to CSV files.

       Parameters:
       - data (pd.DataFrame): Logical coupling data to be saved.
       - repo_name (str): Name of the repository.
       - new_commits_analyzed (list): Newly analyzed commits.
       - commits_analyzed (pd.DataFrame): Previously analyzed commits.
       """
    file = f'.data/{repo_name}/LogicalCoupling.csv'
    file = os.path.relpath(file, os.getcwd())
    data.to_csv(file, index=False)
    file_commits = f'.data/{repo_name}/analyzed.csv'
    file_commits = os.path.relpath(file_commits, os.getcwd())
    new_commits_analyzed = pd.DataFrame({'COMMITS ANALYZED': new_commits_analyzed})
    commits_analyzed = pd.concat([commits_analyzed, new_commits_analyzed])
    commits_analyzed.to_csv(file_commits, index=False)


def run(repo_url, branch, commit_hash, last_commit_analyzed=None):
    """
      Execute the logical coupling tool on a specific repository, branch, and commit.

      Parameters:
      - repo_url (str): URL of the repository.
      - branch (str): Branch name.
      - commit_hash (str): Commit hash to analyze.

      Returns:
      - exit_code (int): Exit code indicating coupling detected (1) or no coupling detected (0).
      - messages (str): Messages indicating coupling detected or empty string if no coupling detected.
      - commits (list): commits in which coupling was detected.
      """
    global logger
    logger = util.setup_logging('logical_coupling')

    try:
        exit_code = 0
        logger.info("Logical coupling tool started")
        initialized_data_path = util.initialize()
        logger.debug(f"Initialized: {initialized_data_path}, absolute path: {os.path.abspath(initialized_data_path)}")

        commit_hash = commit_hash
        branch = branch
        repo_url = repo_url
        repo_name = repo_url.replace('https:', '').replace('git:', '').split('/')[-1].split('.')[0] + "b:" + branch
        # repo_name = repo_url.replace('https:', '').replace('git:', '').split('/')[-1].split('.')[0]

        logger.debug(f"Repo name: {repo_name}")

        path_to_cloned_repo = util.clone(repo_url)

        logger.info(f"Cloned repo: {path_to_cloned_repo}")

        logger.info(f"Loading previous results")

        util.checkout(path_to_cloned_repo, branch, logger)
        util.pull(path_to_cloned_repo, logger)

        data, components_to_ignore, commits_analyzed = load_previous_results(repo_name, path_to_cloned_repo)

        logger.info(f"Loaded previous results")
        logger.debug(f"Data: {data}")
        logger.debug(f"Components to ignore: {components_to_ignore}")

        if commits_analyzed.empty and last_commit_analyzed is None:
            last_commit = None
        else:
            if not commits_analyzed.empty:
                logger.debug(f"Commits analyzed: {commits_analyzed}")
                logger.debug(f"Last commit analyzed: {commits_analyzed.iloc[-1]['COMMITS ANALYZED']}")

                last_commit = commits_analyzed.iloc[-1]['COMMITS ANALYZED']
            elif last_commit_analyzed:
                last_commit = last_commit_analyzed

        new_data, new_commits_analyzed = analyze_commits(path_to_cloned_repo, branch, commit_hash, last_commit,
                                                         components_to_ignore)

        if new_data.empty:
            logger.info("No new coupling found ")
            messages = ""
            commits = []
        else:
            logger.info("New coupling found ")
            exit_code = 1

            alert_data = alert(new_data, data)
            logger.debug(f"Alert data: {alert_data}")
            messages = alert_messages(alert_data)
            commits = new_data['COMMIT']
            new_data.drop('COMMIT', axis=1, inplace=True)
            logger.debug(f"New Data: {new_data}")
            merged_data = update_data(data, new_data)
            save(merged_data, repo_name, new_commits_analyzed, commits_analyzed)
            logger.debug(f"Messages: {messages}")
        logger.info("Logical coupling tool finished")

        return exit_code, messages, []

    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logger.info("Logical coupling tool finished with error")
        return -1, "Error in logical coupling tool", []

    finally:
        logger.debug("Deleting temporary files")
        # shutil.rmtree('.temp/', ignore_errors=True)
