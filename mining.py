import json
import os
import shutil

from git import Repo
from pathlib import Path


class Repository:
    name = ''
    global_path = ''
    local_path = ''
    mining_data = {}
    has_mailmap = False

    def __init__(self, name, global_path, local_path, mining_data, has_mailmap):
        self.name = name
        self.global_path = global_path
        self.local_path = local_path
        self.mining_data = mining_data
        self.has_mailmap = has_mailmap

    def __dict__(self):
        return {
            'name': self.name,
            'global_path': self.global_path,
            'local_path': self.local_path,
            'has_mailmap': self.has_mailmap,
            'mining_data': self.mining_data
        }


repos_list_file = 'data/dummy_repo_base.json'
repos = json.load(open(repos_list_file, 'r'))['items']
os.makedirs('tmp', exist_ok=True)
os.makedirs('results', exist_ok=True)

for repo in repos:
    # Clones repo
    repo_id = repo['name']
    cloning_link = f'https://github.com/{repo_id}.git'
    repo_path = f'tmp/{str(repo_id).split("/")[0] + "_" + str(repo_id).split("/")[1]}'
    git_repo = Repo.clone_from(cloning_link, repo_path)
    print(f'Cloned {repo_id} to {repo_path}')

    # Checks if repo has mailmap
    file_path = Path(f'{repo_path}/.mailmap')
    has_mailmap = file_path.is_file() and file_path.exists()
    print(f'{repo_id} has mailmap: {has_mailmap}')

    # Saves results in json format
    repo_obj = Repository(repo_id, cloning_link, repo_path, repo, has_mailmap)
    with open(f'results/{repo_path[4:]}_results.json', 'w', encoding='utf8') as f:
        json.dump(repo_obj.__dict__(), f, indent=4)

    # Deletes repo
    shutil.rmtree(repo_path)
    print(f'Deleted {repo_path}\n\n')
