import argparse
import jellyfish
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
               f" Commits number: {self.commits_number}, Aliases: {self.aliases}"

    def merge_alias(self, alias):
        self.commits_number += alias.commits_number
        self.aliases.append((alias.name, alias.email))
        self.aliases = self.aliases + alias.aliases
        self.aliases = list(set(self.aliases))


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


def filter_aliases_by_attribute(contributors: List[Contributor], attribute: str):
    data = []

    for contributor in contributors:
        if attribute == 'email':
            _id, domain = contributor.email.rsplit('@', 1)  # the real @ will be the last one
            data.append(_id)
        elif attribute == 'name':
            data.append(contributor.name)
        else:
            raise ValueError(f'Attribute {attribute} is not supported')

    detected_aliases = []
    for i, value in zip(range(len(data)), data):
        if i in detected_aliases:
            continue

        for j in range(len(data)):
            if i == j:
                continue

            if compare_strings(value, data[j]):
                if (j, i) not in detected_aliases:
                    detected_aliases.append((i, j))

    return detected_aliases


def compare_strings(string1, string2):
    # TODO change heuristics to something more sophisticated
    return jellyfish.jaro_distance(string1, string2) > 0.70


def _main(_args):
    if not _args.path:
        print('Enter path to git repository:')
        _args.path = input()

    git_repo = Repository(_args.path)
    commits = git_repo.traverse_commits()
    contributors = get_contributors_set_from_commits(commits)
    print(f'\nContributors before filter names (len = {len(contributors)}):')
    for contributor in contributors:
        print(contributor)

    aliases_by_email = filter_aliases_by_attribute(contributors, 'email')
    print(f'Aliases by email (len = {len(aliases_by_email)}):', aliases_by_email)
    aliases_by_name = filter_aliases_by_attribute(contributors, 'name')
    print(f'Aliases by name (len = {len(aliases_by_name)}):', aliases_by_name)
    aliases = list(set(aliases_by_email + aliases_by_name))
    print(f'Aliases (len = {len(aliases)}):', aliases)

    for i in range(len(contributors)):
        for alias in aliases:
            if i == alias[0]:
                contributors[i].merge_alias(contributors[alias[1]])

    print(f'\nContributors after filter names (len = {len(contributors)}):')
    for contributor in contributors:
        print(contributor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan git repository for contributors, scan for aliases')
    parser.add_argument('-p', '--path', type=str, help='Path to git remote repository')

    args = parser.parse_args()
    _main(args)
