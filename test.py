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