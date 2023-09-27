import json
import os

from git import Repo
from pathlib import Path

# repos_list_file = 'data/dummy_repo_base.json'
# repos = json.load(open(repos_list_file, 'r'))['items']
# os.makedirs('tmp', exist_ok=True)
#
# for repo in repos:
#     repo_id = repo['name']
#     cloning_link = f'https://github.com/{repo_id}.git'
#     git_repo = Repo.clone_from(cloning_link, f'tmp/{str(repo_id).split("/")[0] + "_" + str(repo_id).split("/")[1]}')

for repo in os.listdir('tmp'):
    file_path = Path(f'tmp/{repo}/.mailmap')
    if file_path.is_file() and file_path.exists():
        print(repo, 'exists')
    else:
        print(repo, 'does not exist')
