import os

from git import Repo


def clone(repo_url):
    path = f".temp/{repo_url.replace('/', '_')}"
    Repo.clone_from(repo_url, path)
    return path

def checkout(path_to_repo, branch):
    repo = Repo(path_to_repo)
    git = repo.git
    git.checkout(branch)
    git.for_each_ref()

def root_calculator(file_path: str) -> str:
    path = file_path.lstrip(os.sep)
    root = path[:path.index(os.sep)] if os.sep in path else path
    return root

def initialize():
    if not os.path.exists('../.data'):
        os.mkdir('../.data')


