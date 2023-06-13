import argparse
import json
import os
import csv
import jellyfish
from typing import List
from pydriller import Repository
from collections import defaultdict


class Contributor:
    id = 0
    name = ''
    email = ''
    commits_number = 0
    total_commits = 0
    aliases = []

    def __init__(self, _id, name, email, commits):
        self.id = _id
        self.name = name
        self.email = email
        self.commits_number = len(commits)
        self.total_commits = len(commits)
        self.commits = commits
        self.aliases = []

    def __str__(self):
        return f"Id: {self.id}, Name: {self.name}, Email: {self.email}," \
               f" Commits number: {self.commits_number}, Aliases: {self.aliases}"

    def __iter__(self):
        return iter([self.id, self.name, self.email, self.commits_number])

    def __data__(self):
        return [self.id, self.name, self.email, self.commits_number]

    def __dict__(self, include_aliases=False):
        if include_aliases:
            return {
                'name': self.name,
                'email': self.email,
                'commits_number': self.commits_number,
                'total_commits': self.total_commits,
                'aliases': [alias.__dict__() for alias in self.aliases]
            }
        else:
            return {
                'name': self.name,
                'email': self.email,
                'commits_number': self.commits_number
            }

    def merge_alias(self, alias):
        self.aliases.append(alias)
        self.total_commits += alias.total_commits

    def get_contributor_string(self, include_aliases=False):
        if include_aliases:
            if len(self.aliases) == 0:
                return f"Name: {self.name}, Email: {self.email}," \
                       f" Commits number: {self.commits_number}, Total commits: {self.total_commits}, No Known aliases"

            return f"Name: {self.name}, Email: {self.email}," \
                   f" Commits number: {self.commits_number}, Known aliases: [" \
                   f"{'; '.join([alias.get_contributor_string() for alias in self.aliases])}]" \
                   f" Total commits: {self.total_commits}"

        return f"Name: {self.name}, Email: {self.email}," \
               f" Commits number: {self.commits_number}"


def get_contributors_set_from_commits(commits) -> List[Contributor]:
    contributors = []
    for commit in commits:
        if commit.merge:
            continue

        contributors.append((commit.author.name, commit.author.email))
    contributors_set = set(contributors)

    contributors_list = []
    for index, contributor in enumerate(contributors_set):
        commits_list = []
        for commit in commits:
            # save all commits of the contributor
            if contributor == (commit.author.name, commit.author.email) and not commit.merge:
                commits_list.append(commit)

        contributor_object = Contributor(index, contributor[0], contributor[1], commits_list)
        contributors_list.append(contributor_object)

    return contributors_list


def filter_aliases_by_attribute(contributors: List[Contributor], attribute: str):
    """
    Filter aliases by attribute
    :param contributors: list of contributors
    :param attribute: attribute to filter by
    :return: list of tuples (alias1, alias2) where alias1 and alias2 are indices of contributors that are aliases
    """
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

            if is_alias(value, data[j]):
                if (j, i) not in detected_aliases:
                    detected_aliases.append((i, j))

    return detected_aliases


def is_alias(string1, string2):
    if similarity_measure == 'jaro' or similarity_measure == 'custom':
        return jellyfish.jaro_distance(string1, string2) > (threshold if threshold else 0.70)

    if similarity_measure == 'levenshtein':
        return jellyfish.levenshtein_distance(string1, string2) < (threshold if threshold else 5)

    if similarity_measure == 'hamming':
        return jellyfish.hamming_distance(string1, string2) < (threshold if threshold else 5)


def dfs(adj_list, visited, vertex, result, key):
    visited.add(vertex)
    result[key].append(vertex)
    for neighbor in adj_list[vertex]:
        if neighbor not in visited:
            dfs(adj_list, visited, neighbor, result, key)


def merge_aliases(edges):
    """
    Merge aliases by considering the tuples as edges in a graph and find connected components within the graph
    :param edges: list of tuples (alias1, alias2)
    :return: merged aliases
    """
    #
    adj_list = defaultdict(list)
    for x, y in edges:
        adj_list[x].append(y)
        adj_list[y].append(x)

    result = defaultdict(list)
    visited = set()
    for vertex in adj_list:
        if vertex not in visited:
            dfs(adj_list, visited, vertex, result, vertex)

    return result.values()


def export_contributors(contributors, save_path):
    os.makedirs(save_path, exist_ok=True)

    if output_mode == 'txt':
        with open(os.path.join(save_path, 'list_of_contributors.txt'), 'w', encoding='utf8') as f:
            for contributor in contributors:
                f.write(contributor.get_contributor_string(include_aliases=False) + '\n')
                return

    if output_mode == 'json':
        with open(os.path.join(save_path, 'list_of_contributors.json'), 'w', encoding='utf8') as f:
            json.dump([contributor.__dict__() for contributor in contributors], f, indent=4)
        return

    if output_mode == 'csv':
        with open(os.path.join(save_path, 'list_of_contributors.csv'), 'w', encoding='utf8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['id', 'name', 'email', 'commits'])
            writer.writerows(contributors)
        return


def export_persons(persons, save_path):
    os.makedirs(save_path, exist_ok=True)
    if output_mode == 'txt':
        with open(os.path.join(save_path, 'list_of_persons.txt'), 'w', encoding='utf8') as f:
            for person in persons:
                f.write(person.get_contributor_string(include_aliases=True) + '\n')
        return

    if output_mode == 'json':
        with open(os.path.join(save_path, 'list_of_persons.json'), 'w', encoding='utf8') as f:
            json.dump([person.__dict__(include_aliases=True) for person in persons], f, indent=4)
        return

    if output_mode == 'csv':
        _list = []
        for person in persons:
            person_dict = person.__data__()
            person_dict.append(None)
            _list.append(person_dict)
            for alias in person.aliases:
                alias_dict = alias.__data__()
                alias_dict.append(person.id)
                _list.append(alias_dict)

        with open(os.path.join(save_path, 'list_of_persons.csv'), 'w', encoding='utf8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['id', 'name', 'email', 'commits', 'alias_of'])
            writer.writerows(iter(_list))
        return


def perform_custom_heuristics(persons):
    for person in persons:
        # if the similarity heuristic is not satisfied, then the person has no aliases to check
        if len(person.aliases) == 0:
            continue

        accounts = person.aliases + [person]
        print(f'Checking {person.name} with {len(accounts)} accounts')
        for account in accounts:
            print(f'Checking {account.name} {account.email} with {len(account.commits)} commits')
            for commit in account.commits:
                print(f'Checking commit {commit.hash}, date {commit.author_date},'
                      f' branch {commit.branches}, files {commit.files}')
        print('------------------')
        break


def _main(_args):
    """
    Main function
    :param _args: command line arguments
    :return:
    """
    git_repo = Repository(_args.repo_path, only_no_merge=True)
    commits = list(git_repo.traverse_commits())
    contributors = get_contributors_set_from_commits(commits)

    if _args.attribute == 'all':
        aliases_by_email = filter_aliases_by_attribute(contributors, 'email')
        aliases_by_name = filter_aliases_by_attribute(contributors, 'name')
        aliases = list(set(aliases_by_email + aliases_by_name))
        aliases = sorted(aliases, key=lambda x: x[0])
        aliases = merge_aliases(aliases)
    else:
        aliases = filter_aliases_by_attribute(contributors, _args.attribute)
        aliases = sorted(aliases, key=lambda x: x[0])

    index_to_delete = []
    for alias in aliases:
        for i in range(1, len(alias)):
            contributors[alias[0]].merge_alias(contributors[alias[i]])
            index_to_delete.append(alias[i])

    persons = [contributors[i] for i in range(len(contributors)) if i not in index_to_delete]

    if similarity_measure == 'custom':
        perform_custom_heuristics(persons)

    export_contributors(contributors, _args.output_path)
    export_persons(persons, _args.output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan git repository for contributors, scan for aliases')
    parser.add_argument('-p', '--repo-path', type=str, help='Path to git remote repository', required=True)
    parser.add_argument('-o', '--output-path', type=str, help='Path to save results', required=True)
    parser.add_argument('-om', '--output-mode', type=str, help='Output mode, default is json', default='json',
                        choices=['json', 'csv', 'txt'])
    parser.add_argument('-m', '--similarity-measure', type=str, help='Similarity measure to use, default is custom' +
                                                                     ' (jaro with some post processing)',
                        default='custom', choices=['jaro', 'levenshtein', 'hamming', 'custom'])
    parser.add_argument('-t', '--threshold', type=float, help='Threshold for similarity measure, default is' +
                                                              ' > 0.70 for jaro, < 5 for levenshtein and hamming')
    parser.add_argument('-a', '--attribute', type=str, help='Attribute to use for alias detection, default is all',
                        default='all', choices=['all', 'email', 'name'])

    args = parser.parse_args()
    output_mode = args.output_mode
    similarity_measure = args.similarity_measure
    threshold = args.threshold
    _main(args)
