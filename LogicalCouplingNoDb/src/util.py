import logging
import os
from logging.handlers import TimedRotatingFileHandler

from git import Repo


def clone(repo_url):
    path = f".temp/{repo_url.replace('/', '_').replace(' https://', '')}"
    print(os.path.relpath(path, os.getcwd()))
    print(os.path.abspath(path))
    Repo.clone_from(repo_url, path)
    return path


def checkout(path_to_repo, branch, logger):
    logger.debug(f"Path to repo: {path_to_repo}")
    logger.debug(f"Checking out branch {branch}")
    repo = Repo(path_to_repo)
    git = repo.git
    git.checkout(branch)
    git.for_each_ref()
    logger.info(f"Checked out branch {branch}")


def root_calculator(file_path: str) -> str:
    path = file_path.lstrip(os.sep)
    root = path[:path.index(os.sep)] if os.sep in path else path
    return root


def initialize():
    data = os.path.relpath('.data', os.getcwd())

    if not os.path.exists(data):
        os.mkdir(data)
    return data


def setup_logging(route_name):
    logger = logging.getLogger(route_name)
    # Check if the logger already has handlers

    if not logger.hasHandlers():
        os.makedirs(route_name, exist_ok=True)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        error_handler = TimedRotatingFileHandler(f'{route_name}/error.log', when='midnight', interval=1, backupCount=7,
                                                 encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        log_handler = TimedRotatingFileHandler(f'{route_name}/log.log', when='midnight', interval=1, backupCount=7,
                                               encoding='utf-8')
        log_handler.setLevel(logging.INFO)
        log_handler.setFormatter(formatter)

        debug_handler = TimedRotatingFileHandler(f'{route_name}/debug.log', when='midnight', interval=1, backupCount=7,
                                                 encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)

        logger.addHandler(error_handler)
        logger.addHandler(log_handler)
        logger.addHandler(debug_handler)

    return logger
