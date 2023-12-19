from GitExtractor import GitExtractor
from LogicalCouplingCalculator import LogicalCouplingCalculator
import argparse


def main(repo_url, branch, commit):
    print("Extracting Modified Files from git")
    files = GitExtractor(repo_url, branch, commit).extract()
    print("Calculating Coupling")
    LogicalCouplingCalculator().calculate(files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("commit_hash")
    parser.add_argument("branch")
    parser.add_argument("repo_url")
    args = parser.parse_args()
    print(args.repo_url, args.branch, args.commit_hash)

    main(args.repo_url, args.branch, args.commit_hash)

