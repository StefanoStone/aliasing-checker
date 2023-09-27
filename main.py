import argparse
import json
import os
import re
import csv
import jellyfish
import datetime
import subprocess

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


def extract_name_from_email(email):
    # check with regex if the email is valid
    if not re.match(r"^[\w\-\.]+@([\w-]+\.)+[\w-]{2,}$", email):
        return email

    name, domain = email.rsplit('@', 1)  # the real @ will be the last one
    return name


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
            data.append(extract_name_from_email(contributor.email))
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

            if is_alias(value, data[j], similarity_measure, threshold):
                if (j, i) not in detected_aliases:
                    detected_aliases.append((i, j))

    return detected_aliases


def is_alias(string1, string2, measure, _threshold):
    if measure == 'jaro' or measure == 'custom':
        return jellyfish.jaro_similarity(string1, string2) > (_threshold if _threshold else 0.70)

    if measure == 'levenshtein':
        return jellyfish.levenshtein_distance(string1, string2) < (_threshold if _threshold else 5)

    if measure == 'hamming':
        return jellyfish.hamming_distance(string1, string2) < (_threshold if _threshold else 5)


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


def export_contributors(contributors, save_path, name='list_of_contributors', output_mode='json'):
    os.makedirs(save_path, exist_ok=True)

    if output_mode == 'txt':
        with open(os.path.join(save_path, f'{name}.txt'), 'w', encoding='utf8') as f:
            for contributor in contributors:
                f.write(contributor.get_contributor_string(include_aliases=False) + '\n')
        return

    if output_mode == 'json':
        with open(os.path.join(save_path, f'{name}.json'), 'w', encoding='utf8') as f:
            json.dump([contributor.__dict__() for contributor in contributors], f, indent=4)
        return

    if output_mode == 'csv':
        with open(os.path.join(save_path, f'{name}.csv'), 'w', encoding='utf8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['id', 'name', 'email', 'commits'])
            writer.writerows(contributors)
        return


def export_people(people, save_path, name='list_of_people'):
    os.makedirs(save_path, exist_ok=True)
    if output_mode == 'txt':
        with open(os.path.join(save_path, f'{name}.txt'), 'w', encoding='utf8') as f:
            for person in people:
                f.write(person.get_contributor_string(include_aliases=True) + '\n')
        return

    if output_mode == 'json':
        with open(os.path.join(save_path, f'{name}.json'), 'w', encoding='utf8') as f:
            json.dump([person.__dict__(include_aliases=True) for person in people], f, indent=4)
        return

    if output_mode == 'csv':
        # puts a column named alias_of at the end of the csv file, which is the id of the person that the alias belongs
        # to if the alias belongs to a person, otherwise it is None
        _list = []
        for person in people:
            person_dict = person.__data__()
            person_dict.append(None)
            _list.append(person_dict)
            for alias in person.aliases:
                alias_dict = alias.__data__()
                alias_dict.append(person.id)
                _list.append(alias_dict)

        with open(os.path.join(save_path, f'{name}.csv'), 'w', encoding='utf8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['id', 'name', 'email', 'commits', 'alias_of'])
            writer.writerows(iter(_list))
        return


def get_working_branches(contributor):
    branches = []
    for commit in contributor.commits:
        branches.extend(commit.branches)

    return list(set(branches))


def get_working_files(contributor):
    files = []
    for commit in contributor.commits:
        files.extend(commit.modified_files)

    return list(set(files))


def get_working_date_range(contributor):
    dates = []
    for commit in contributor.commits:
        dates.append(commit.committer_date)

    return min(dates), max(dates)


def perform_custom_heuristics(people):
    new_people = []
    week_delta = datetime.timedelta(days=7)

    for person in people:
        # if the similarity heuristic is not satisfied, then the person has no aliases to check
        if len(person.aliases) == 0:
            new_people.append(person)
            continue

        try:
            person_branches = get_working_branches(person)
            person_files = get_working_files(person)
            person_start_date, person_end_date = get_working_date_range(person)
        except Exception as e:
            raise Exception('Error while performing custom heuristics, something went wrong with pydriller')

        for alias in person.aliases:
            # if the alias has the same name or email as the person, then it is an alias
            if alias.name == person.name or alias.email == person.email:
                continue

            # if the alias has more than 20 commits, it is probably not an alias
            if len(alias.commits) > 20:
                new_people.append(alias)
                person.aliases.remove(alias)
                continue

            # if the alias worked on different branches than the person, then it is probably not an alias
            alias_branches = get_working_branches(alias)
            if len(set(person_branches).intersection(set(alias_branches))) == 0:
                new_people.append(alias)
                person.aliases.remove(alias)
                continue

            # if the alias worked on different files than the person, then it is probably not an alias
            alias_files = get_working_files(alias)
            if len(set(person_files).intersection(set(alias_files))) == 0:
                new_people.append(alias)
                person.aliases.remove(alias)
                continue

            # if the alias worked on different dates than the person, then it is probably not an alias
            # consider a week delta to account for the fact that the person and the alias might have worked
            # on the same project, but at different times
            alias_start_date, alias_end_date = get_working_date_range(alias)
            if alias_start_date > (person_end_date + week_delta) \
                    or alias_end_date < (person_start_date + week_delta):
                new_people.append(alias)
                person.aliases.remove(alias)
                continue

        new_people.append(person)

    return new_people


def init_git_submodules(repo_name):
    """
    Initializes and clones the git submodules of a repository
    :param repo_name:
    :return:
    """
    p = subprocess.Popen(['git', 'submodule', 'init'], cwd='/tmp/{}'.format(repo_name),
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.STDOUT)
    p.wait()
    p = subprocess.Popen(['git', 'submodule', 'update'], cwd='/tmp/{}'.format(repo_name),
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.STDOUT)
    p.wait()


def _main(_args):
    """
    Main function
    :param _args: command line arguments
    :return:
    """
    os.makedirs('/tmp', exist_ok=True)
    git_repo = Repository(_args.repo_path, only_no_merge=True, clone_repo_to='/tmp')
    repo_name = _args.repo_path.split('/')[-1]

    if os.path.exists('./tmp/{}/.gitmodules'.format(repo_name)):
        init_git_submodules(repo_name)

    commits = list(git_repo.traverse_commits())
    contributors = get_contributors_set_from_commits(commits)

    # gather aliases based on the attributes selected by the user
    if _args.attribute == 'all':
        aliases_by_email = filter_aliases_by_attribute(contributors, 'email')
        aliases_by_name = filter_aliases_by_attribute(contributors, 'name')
        aliases = list(set(aliases_by_email + aliases_by_name))
        aliases = sorted(aliases, key=lambda x: x[0])
        aliases = merge_aliases(aliases)
    else:
        aliases = filter_aliases_by_attribute(contributors, _args.attribute)
        aliases = sorted(aliases, key=lambda x: x[0])

    # group aliases in person objects (the person will be the contributor with the most commits)
    index_to_delete = []
    for alias_group in aliases:
        index_with_highest_commits = 0
        for index, alias_index in enumerate(alias_group):
            if contributors[alias_index].commits_number > \
                    contributors[alias_group[index_with_highest_commits]].commits_number:
                index_with_highest_commits = index

        for i in range(0, len(alias_group)):
            if i == index_with_highest_commits:
                continue

            contributors[alias_group[index_with_highest_commits]].merge_alias(contributors[alias_group[i]])
            index_to_delete.append(alias_group[i])

    people = [contributors[i] for i in range(len(contributors)) if i not in index_to_delete]

    # perform custom heuristics to remove false positives
    if similarity_measure == 'custom':
        try:
            people = perform_custom_heuristics(people)
        except Exception as e:
            # shutil.rmtree('/tmp/{}'.format(repo_name))
            print('Error while performing custom heuristics, something went wrong with pydriller'
                  'try using a different similarity measure')

    # save results in the desired format
    export_contributors(contributors, _args.output_path)
    export_people(people, _args.output_path)

    # TODO remove the cloned repository
    # shutil.rmtree('/tmp/{}'.format(repo_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan git repository for contributors, scan for aliases')
    parser.add_argument('-p', '--repo-path', type=str, help='Path to git repository (local or remote)', required=True)
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
    # TODO finish implementing this argument
    # parser.add_argument('-on', '--output-name', type=str, help='Output name, default is list_of_{item}')

    args = parser.parse_args()
    output_mode = args.output_mode
    similarity_measure = args.similarity_measure
    threshold = args.threshold
    _main(args)
