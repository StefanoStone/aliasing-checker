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

            if compare_strings(value, data[j]) > 0.70:
                contributors[i].merge_alias(contributors[j])
                detected_aliases.append(j)

    contributors = list(filter(lambda x: contributors.index(x) not in detected_aliases, contributors))

    return contributors


def compare_strings(string1, string2):
    # TODO change heuristics to something more sophisticated
    return jellyfish.jaro_distance(string1, string2)


def _main(_args):
    if not _args.path:
        print('Enter path to git repository:')
        _args.path = input()

    git_repo = Repository(_args.path)
    commits = git_repo.traverse_commits()
    contributors = get_contributors_set_from_commits(commits)
    print(f'Contributors before filter names (len = {len(contributors)}):')
    for contributor in contributors:
        print(contributor)

    filtered_contributors = filter_aliases_by_attribute(contributors, 'email')
    print('\n')
    print('\n')
    print(f'Contributors after filter email (len = {len(filtered_contributors)}):')
    for contributor in filtered_contributors:
        print(contributor)

    filtered_contributors = filter_aliases_by_attribute(filtered_contributors, 'name')
    print('\n')
    print('\n')
    print(f'Contributors after filter names (len = {len(filtered_contributors)}):')
    for contributor in filtered_contributors:
        print(contributor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan git repository for contributors, scan for aliases')
    parser.add_argument('-p', '--path', type=str, help='Path to git remote repository')

    args = parser.parse_args()
    _main(args)
