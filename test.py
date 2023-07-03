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


def test_get_files():
    git_repo = Repository('test_repos/complex_repo')
    commits = list(git_repo.traverse_commits())
    contributors = get_contributors_set_from_commits(commits)
    files = get_working_files(contributors[0])
    files_names = [file.filename for file in files if file.filename.endswith('.java')
                   or file.filename.endswith('.javax')]
    set_files_names = set(files_names)
    expected_files = ['Secao.java', 'Arquivo.java', 'Capitulo.java', 'Aluno.java',
                      'Secao.javax', 'Matricula.javax', 'Matricula.java']
    assert set_files_names == set(expected_files) and len(files) == 15


def test_alias_merge():
    user1 = Contributor(1, 'test1', 'test1@test.com', [1, 2])
    user2 = Contributor(2, 'test2', 'test2@test.com', [3, 4])
    user1.merge_alias(user2)

    assert user1.total_commits == 4 and len(user1.aliases) == 1 and user1.aliases[0].id == 2
