from main import Contributor, export_contributors
from git import Repo

repo = Repo.init('./test_repos/OpenDDS')
commits = list(repo.iter_commits('master'))
contributors = list()

for commit in commits:
    contributors.append((commit.author.name, commit.author.email))
contributors_set = set(contributors)

contributors_list = []
for index, contributor in enumerate(contributors_set):
    commits_list = []
    for commit in commits:
        # save all commits of the contributor
        if contributor == (commit.author.name, commit.author.email) and commit.type == 'commit':
            commits_list.append(commit)

    contributor_object = Contributor(index, contributor[0], contributor[1], commits_list)
    contributors_list.append(contributor_object)

export_contributors(contributors_list, 'out/dds')
