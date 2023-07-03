import datetime

from main import *


def test_alias_jaro():
    results = is_alias("alias", "alias", 'jaro', 0.7)
    assert results == True


def test_alias_custom():
    results = is_alias("alias", "alias", 'custom', 0.7)
    assert results == True


def test_alias_levenshtein():
    results = is_alias("alias", "alias", 'levenshtein', 5)
    assert results == True


def test_alias_hamming():
    results = is_alias("alias", "alias", 'hamming', 5)
    assert results == True


def test_alias_jaro_false():
    results = is_alias("alias", "name", 'jaro', 0.7)
    assert results == False


def test_alias_custom_false():
    results = is_alias("alias", "name", 'custom', 0.7)
    assert results == False


def test_alias_levenshtein_false():
    results = is_alias("alias", "name", 'levenshtein', 5)
    assert results == False


def test_alias_hamming_false():
    results = is_alias("alias", "name", 'hamming', 5)
    assert results == False


def test_merge_alias():
    edges = [(5, 15), (8, 52), (23, 49), (23, 24)]
    expected_results = {
        3: [5, 15], 2: [8, 52], 1: [23, 49, 24]
    }.values()
    results = merge_aliases(edges)
    assert list(results) == list(expected_results)


def test_extract_name():
    email = "test@test.com"
    expected_name = "test"
    name = extract_name_from_email(email)
    assert name == expected_name


def test_extract_name_false():
    email = "test@test.com"
    expected_name = "test1"
    name = extract_name_from_email(email)
    assert name != expected_name


def test_get_contributors():
    git_repo = Repository('test_repos/complex_repo')
    commits = list(git_repo.traverse_commits())
    contributors = get_contributors_set_from_commits(commits)
    assert len(contributors) == 1 and contributors[0].name == 'Maurício Aniche'\
           and contributors[0].email == 'mauricioaniche@gmail.com'


def test_get_branches():
    git_repo = Repository('test_repos/complex_repo')
    commits = list(git_repo.traverse_commits())
    contributors = get_contributors_set_from_commits(commits)
    branches = get_working_branches(contributors[0])
    expected_branches = ['master', 'b2']
    assert set(branches) == set(expected_branches)


def test_get_dates():
    git_repo = Repository('test_repos/complex_repo')
    commits = list(git_repo.traverse_commits())
    contributors = get_contributors_set_from_commits(commits)
    start, end = get_working_date_range(contributors[0])
    expected_start = datetime.datetime(2014, 9, 26, 1, 22, 43)
    expected_end = datetime.datetime(2015, 7, 21, 11, 38, 40)
    # remove timezone from datetime
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)

    assert start == expected_start and end == expected_end

