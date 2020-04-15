"""Unit Tests - test API."""
from pathlib import Path

import libsast


def get_config():
    base_dir = Path(__file__).parents[0]
    rules_dir = base_dir / 'assets' / 'rules'
    files_dir = base_dir / 'assets' / 'files'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    return options, paths


def test_no_rule():
    assert libsast.PatternMatcher({}).scan([]) is None


def test_no_path():
    options, _ = get_config()
    assert libsast.PatternMatcher(options).scan([]) == {}


def test_pattern_matcher():
    options, paths = get_config()
    result = libsast.PatternMatcher(options).scan(paths)
    assert result['test_regex_or']


def test_scanner():
    options, paths = get_config()
    result = libsast.Scanner(options, paths).scan()
    assert result['pattern_matcher']['test_regex']


def test_scanner_file():
    options, paths = get_config()
    file_path = [paths[0] + '/test_matcher.test']
    result = libsast.Scanner(options, file_path).scan()
    assert result['pattern_matcher']['test_regex']
