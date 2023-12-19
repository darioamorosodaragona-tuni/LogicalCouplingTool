from pydriller import Repository


class GitExtractor:
    def __init__(self, repo_url, branch, commit):
        self.repo_url = repo_url
        self.branch = branch
        self.commit = commit

    def extract(self) -> list[str]:
        repo = Repository(self.repo_url, single=self.commit, only_in_branch=self.branch)
        modified_files = []
        result = []

        for commit in repo.traverse_commits():
            modified_files = commit.modified_files

        for files in modified_files:
            result.append(files.new_path)

        return result
