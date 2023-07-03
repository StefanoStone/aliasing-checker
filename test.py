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