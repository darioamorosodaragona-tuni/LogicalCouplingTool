import logging
import os
from logging.handlers import TimedRotatingFileHandler
from urllib.parse import urlparse
from git import Repo

# Define base paths
DATA_PATH = '/app/.data'
TEMP_PATH = '/app/.tmp'
ROOT = '/app/'

def is_remote_git_repo(repo_path):
    # Check if it's a URL
    parsed_url = urlparse(repo_path)
    if parsed_url.scheme and parsed_url.netloc:
        # Assuming it's a remote Git repository URL
        return True
    # Check if it's a local path
    if os.path.exists(repo_path) and os.path.isdir(repo_path):
        # Assuming it's a local Git repository path
        return False
    # Not a valid remote URL or local path
    raise ValueError("Invalid Git repository path: {}".format(repo_path))

def clone(repo_url):
    path = os.path.join(TEMP_PATH, repo_url.replace('https://', '').replace('/', '_'))
    if not os.path.exists(path):
        if is_remote_git_repo(repo_url):
            logging.debug(f"relative path to cloning: {os.path.relpath(path, os.getcwd())}")
            logging.debug(f"absolute path to cloning: {os.path.abspath(path)}")
            Repo.clone_from(repo_url, path)
            return path
        else:
            return repo_url
    else:
        return path

def pull(path_to_repo, logger):
    logger.debug(f"Path to repo: {path_to_repo}")
    logger.info(f"Pulling repo")
    repo = Repo(path_to_repo)
    repo.remotes.origin.pull()

def checkout(path_to_repo, branch, logger):
    logger.debug(f"Path to repo: {path_to_repo}")
    logger.debug(f"Checking out branch {branch}")
    repo = Repo(path_to_repo)
    git = repo.git
    git.checkout(branch)
    git.for_each_ref()
    logger.info(f"Checked out branch {branch}")

def root_calculator(file_path: str) -> str:
    root = file_path.rsplit(os.sep, 1)[0] if os.sep in file_path else file_path
    return root

# def initialize():
#     if not os.path.exists(DATA_PATH):
#         os.makedirs(DATA_PATH)
#     if not os.path.exists(TEMP_PATH):
#         os.makedirs(TEMP_PATH)
#     return DATA_PATH, TEMP_PATH

def initialize():
    data = os.path.relpath(DATA_PATH, os.getcwd())
    if not os.path.exists(data):
        os.mkdir(data)
    return data

def setup_logging(route_name):
    logger = logging.getLogger(route_name)
    # Check if the logger already has handlers

    if not logger.hasHandlers():
        path = os.path.join(ROOT, route_name)
        os.makedirs(path, exist_ok=True)

        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        error_handler = TimedRotatingFileHandler(f'{path}/error.log', when='midnight', interval=1, backupCount=7, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        log_handler = TimedRotatingFileHandler(f'{path}/log.log', when='midnight', interval=1, backupCount=7, encoding='utf-8')
        log_handler.setLevel(logging.INFO)
        log_handler.setFormatter(formatter)

        debug_handler = TimedRotatingFileHandler(f'{path}/debug.log', when='midnight', interval=1, backupCount=7, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        logger.addHandler(error_handler)
        logger.addHandler(log_handler)
        logger.addHandler(debug_handler)
        logger.addHandler(console_handler)

        logger.debug(f"Logging initialized for {route_name} in {path}")

    return logger
