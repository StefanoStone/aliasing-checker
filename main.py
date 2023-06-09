import argparse
from typing import List
from pydriller import Repository


class Contributor:
    name = ''
    email = ''
    commits_number = 0
    aliases = []

    def __init__(self, name, email, commits_number):
        self.name = name
        self.email = email
        self.commits_number = commits_number
        self.aliases = []

    def __str__(self):
        return f"Name: {self.name}, Email: {self.email}," \
               f" Commits number: {self.commits_number}"


def get_contributors_set_from_commits(commits) -> List[Contributor]:
    contributors = []
    for commit in commits:
        contributors.append((commit.author.name, commit.author.email))
    contributors_set = set(contributors)

    contributors_list = []
    for contributor in contributors_set:
        contributor_object = Contributor(contributor[0], contributor[1], contributors.count(contributor))
        contributors_list.append(contributor_object)

    return contributors_list


def _main(_args):
    if not _args.path:
        print('Enter path to git repository:')
        _args.path = input()

    git_repo = Repository(_args.path)
    commits = git_repo.traverse_commits()
    contributors = get_contributors_set_from_commits(commits)
    for contributor in contributors:
        print(contributor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan git repository for contributors, scan for aliases')
    parser.add_argument('-p', '--path', type=str, help='Path to git remote repository')

    args = parser.parse_args()
    _main(args)
