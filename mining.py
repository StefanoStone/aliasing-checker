import json
import os

from git import Repo
from pathlib import Path


class Repository:
    name = ''
    global_path = ''
    local_path = ''
    has_mailmap = False

    def __init__(self, name, global_path, local_path, has_mailmap):
        self.name = name
        self.global_path = global_path
        self.local_path = local_path
        self.has_mailmap = has_mailmap

    def __dict__(self):
        return {
            'name': self.name,
            'global_path': self.global_path,
            'local_path': self.local_path,
            'has_mailmap': self.has_mailmap
        }


repos_list_file = 'data/dummy_repo_base.json'
repos = json.load(open(repos_list_file, 'r'))['items']
os.makedirs('tmp', exist_ok=True)

results = []
for repo in repos:
    repo_id = repo['name']
    cloning_link = f'https://github.com/{repo_id}.git'
    repo_path = f'tmp/{str(repo_id).split("/")[0] + "_" + str(repo_id).split("/")[1]}'
    # git_repo = Repo.clone_from(cloning_link, repo_path)
    print(f'Cloned {repo_id} to {repo_path}')

    file_path = Path(f'{repo_path}/.mailmap')
    has_mailmap = file_path.is_file() and file_path.exists()
    print(f'{repo_id} has mailmap: {has_mailmap}')

    repo_obj = Repository(repo_id, cloning_link, repo_path, has_mailmap)
    results.append(repo_obj)

with open('results.json', 'w', encoding='utf8') as f:
    json.dump([repo.__dict__() for repo in results], f, indent=4)
