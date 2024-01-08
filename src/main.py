from GitExtractor import GitExtractor
from LogicalCouplingCalculator import LogicalCouplingCalculator
import argparse

from src import Core

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit_hash")
    parser.add_argument("--branch")
    parser.add_argument("--repo_url")
    parser.add_argument("--db_username")
    parser.add_argument("--db_password")
    parser.add_argument("--db_url")
    parser.add_argument("--db_port")
    parser.add_argument("--project_name")

    args = parser.parse_args()
    print(args.repo_url, args.branch, args.commit_hash)

    Core.run(args.branch, args.project_name, args.repo_url, args.commit_hash, args.db_url, args.db_port, args.db_username, args.db_password)