import argparse
from pydriller import *


def _main(_args):
    if not _args.path:
        print('Enter path to git repository:')
        _args.path = input()

    git_repo = Repository(_args.path)
    commits = git_repo.traverse_commits()
    for commit in commits:
        print(commit.hash)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan git repository for contributors, scan for aliases')
    parser.add_argument('-p', '--path', type=str, help='Path to git remote repository')

    args = parser.parse_args()
    _main(args)
