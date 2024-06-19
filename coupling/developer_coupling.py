import fnmatch
import os
import shutil
import traceback

from pandas import DataFrame
import pydriller
#
# from coupling import util
# from coupling.util import clone, checkout, initialize, root_calculator
import util
from util import clone, checkout, initialize, root_calculator

logger = util.setup_logging('developer_coupling')


def load_previous_results(path_to_data, path_to_repo, branch, path_to_dev_ignore_file, path_to_comp_ignore_file):
    result = []

    if os.path.exists(path_to_data):
        logger.info("Previous results found")
        logger.debug("Previous results found in " + os.path.abspath(path_to_data))

        result = os.listdir(path_to_data)
        logger.debug(f"Previous results: {result}")
        logger.info(f"Previous results loaded")



    else:
        logger.info("No previous results found")
        os.makedirs(path_to_data, exist_ok=True)
        logger.debug("Created directory for results: " + os.path.abspath(path_to_data))


    component_to_ignore = []
    developer_to_ignore = []
    if os.path.exists(path_to_comp_ignore_file):
        logger.info("Components ignore file found")
        with open(path_to_comp_ignore_file, 'r') as file:
            lines = file.readlines()

        component_to_ignore = [line.strip() for line in lines]
        logger.debug(f"Components to ignore: {component_to_ignore}")

    if os.path.exists(path_to_dev_ignore_file):
        logger.info("Developers ignore file found")
        with open(path_to_dev_ignore_file, 'r') as file:
            lines = file.readlines()

        developer_to_ignore = [line.strip() for line in lines]
        logger.debug(f"Developers to ignore: {developer_to_ignore}")

    component_to_ignore.append('.dev_comp_ignore')
    component_to_ignore.append('.devignore')

    return result, component_to_ignore, developer_to_ignore


def analyze_and_save_actual_commit(path_to_repo, branch, commit_hash, components_to_ignore, devs_to_ignore, data,
                                   path_to_data):
    roots = []
    developer = ""
    logger.info(f"Analyzing commit {commit_hash} on branch {branch}")

    for commit in pydriller.Repository(path_to_repo, only_commits=commit_hash, only_in_branch=branch).traverse_commits():

        if commit.author.email in devs_to_ignore:
            logger.debug(f"Developer {commit.author.email} ignored")
            return DataFrame(
                {'COMPONENT': [], 'DEVELOPER': []})

        modified_files = commit.modified_files

        for files in modified_files:
            logger.debug(f"Modified file: {files.new_path}")
            if not any(fnmatch.fnmatch(files.new_path, pattern) for pattern in components_to_ignore):
                logger.debug(f"File {files.new_path} not ignored")
                roots.append(files.new_path)
                developer = commit.author.email
            else:
                logger.debug(f"Ignored file: {files.new_path}")

    # components = [root_calculator(file_path) for file_path in result]
    components = []
    for file_path in roots:
        components.append(root_calculator(file_path))

    logger.debug(f"Components: {components}")

    components_to_alert = []

    logger.debug(f"Previous results: {data}")
    for component in components:
        logger.debug(f"Analyzing Component: {component}")
        if component in data:
            logger.debug(f"Component {component} found in previous results")
            with open(f"{path_to_data}/{component}", 'r') as file:
                lines = file.readlines()
            developers = [line.strip() for line in lines]
            logger.debug(f"Developers for {component}: {developers}")

            if developer not in developers:
                logger.debug(f"Developer {developer} not found in previous results for component {component}")
                components_to_alert.append(component)

                with open(f"{path_to_data}/{component}", 'a') as file:
                    logger.debug(f"Adding developer {developer} to component {component}")
                    file.write(developer + '\n')
        else:
            logger.debug(f"Component {component} not found in previous results")
            with open(f"{path_to_data}/{component}", 'w') as file:
                logger.debug(f"Created file {path_to_data}/{component}")
                logger.debug(f"Adding developer {developer} to component {component}")
                file.write(developer + '\n')

    return DataFrame({'COMPONENT': components_to_alert, 'DEVELOPER': [developer] * len(components_to_alert)})


def alert_message(data):
    messages = ""
    for index, row in data.iterrows():
        messages += f"Developer {row['DEVELOPER']} modified component {row['COMPONENT']} for the first time\n"
    return messages


def run(repo_url, branch, commit_hash):
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

        path_to_data = f'.data/{repo_name}/developer_coupling'
        path_to_data = os.path.relpath(path_to_data, f'{os.getcwd()}')

        path_to_cloned_repo = clone(repo_url)

        logger.info(f"Cloned repo: {path_to_cloned_repo}")

        path_to_dev_ignore_file = f'{path_to_cloned_repo}/.devignore'
        path_to_comp_ignore_file = f'{path_to_cloned_repo}/.dev_comp_ignore'

        logger.debug(f"Path to dev ignore file: {path_to_dev_ignore_file}")
        logger.debug(f"Path to comp ignore file: {path_to_comp_ignore_file}")

        logger.info(f"Loading previous results")

        util.checkout(path_to_cloned_repo, branch, logger)
        util.pull(path_to_cloned_repo, logger)

        data, components_to_ignore, developers_to_ignore = load_previous_results(path_to_data,
                                                                                 path_to_cloned_repo,
                                                                                 branch,
                                                                                 path_to_dev_ignore_file,
                                                                                 path_to_comp_ignore_file)
        logger.info(f"Loaded previous results")
        logger.debug(f"Data: {data}")
        logger.debug(f"Components to ignore: {components_to_ignore}")
        logger.debug(f"Developers to ignore: {developers_to_ignore}")

        new_data = analyze_and_save_actual_commit(path_to_cloned_repo, branch, commit_hash, components_to_ignore,
                                                  developers_to_ignore, data, path_to_data)

        logger.info(f"Analyzed actual commit")
        logger.debug(f"New data: new_data")
        message = alert_message(new_data)
        logger.debug(f"Message: {message}")

        if not new_data.empty:
            logger.info("New coupling found")
            exit_code = 1, message

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(e)
        logger.debug(f"Error in developer coupling tool")
        logger.debug(traceback.format_exc())
        exit_code = -1
        message = "Error in developer coupling tool"
        logger.info("Error in developer coupling tool")

    finally:
        logger.debug("Removing temporary files")
        # shutil.rmtree('.temp/', ignore_errors=True)

    logger.info("Developer coupling tool finished")
    return exit_code, message, []
