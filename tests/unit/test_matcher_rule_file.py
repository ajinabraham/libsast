"""Unit Tests - test pattern matcher rule file loading."""
from pathlib import Path

import libsast


def test_load_dir():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rules_dir = base_dir / 'assets' / 'rules'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    assert libsast.PatternMatcher(options).scan(paths)['test_regex_or']


def test_load_multiple_rules():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rules_dir = base_dir / 'assets' / 'multiple'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    result = libsast.PatternMatcher(options).scan(paths)
    assert result['test_regex_or']
    assert result['test_regex']
    assert result['test_regex_and']
    assert result['test_regex_or']
    assert result['test_regex_and_not']
    assert result['test_regex_or']


def test_load_file():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'rules' / 'patterns.yaml'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    assert libsast.PatternMatcher(options).scan(paths)['test_regex_or']


def test_load_url():
    rule_url = ('https://raw.githubusercontent.com/ajinabraham/'
                'libsast/master/tests/unit/assets/rules/patterns.yaml')
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    options = {'match_rules': rule_url}
    paths = [files_dir.as_posix()]
    assert libsast.PatternMatcher(options).scan(paths)['test_regex_or']


def test_load_invalid_url():
    rule_url = ('https://raw.githubusercontent.com/ajinabraham/'
                'libsast/master/tests/unit/assets/rules')
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    options = {'match_rules': rule_url}
    paths = [files_dir.as_posix()]
    assert libsast.PatternMatcher(options).scan(paths) is None


def test_load_file_invalid_path():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'rules' / 'patterns.yoo'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    assert libsast.PatternMatcher(options).scan(paths) is None


def test_load_file_invalid_yaml():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'invalid' / 'invalid.yaml'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    assert libsast.PatternMatcher(options).scan(paths) == {}
