"""Unit Tests - test API."""
from pathlib import Path

import libsast


def get_config():
    base_dir = Path(__file__).parents[0]
    rules_dir = base_dir / 'assets' / 'rules' / 'pattern_matcher'
    files_dir = base_dir / 'assets' / 'files'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    return options, paths


def test_no_rule():
    assert libsast.Scanner({}, []).scan() is None


def test_no_path():
    options, _ = get_config()
    assert libsast.Scanner(options, []).scan() is None


def test_pattern_matcher_dir():
    options, paths = get_config()
    result = libsast.Scanner(options, paths).scan()
    assert result['pattern_matcher']['test_regex_or']


def test_pattern_matcher_file():
    options, paths = get_config()
    file_path = [paths[0] + '/test_matcher.test']
    result = libsast.Scanner(options, file_path).scan()
    assert result['pattern_matcher']['test_regex']
