"""Unit Tests - test pattern matcher rule file loading."""
from pathlib import Path

import libsast

import pytest


def test_load_dir():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rules_dir = base_dir / 'assets' / 'rules'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    res = libsast.Scanner(options, paths).scan()
    assert res['pattern_matcher']['test_regex_or']


def test_load_multiple_rules():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rules_dir = base_dir / 'assets' / 'multiple'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    res = libsast.Scanner(options, paths).scan()['pattern_matcher']
    assert res['test_regex_or']
    assert res['test_regex']
    assert res['test_regex_and']
    assert res['test_regex_or']
    assert res['test_regex_and_not']
    assert res['test_regex_or']


def test_load_file():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'rules' / 'patterns.yaml'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    res = libsast.Scanner(options, paths).scan()
    assert res['pattern_matcher']['test_regex_or']


def test_load_url():
    rule_url = ('https://raw.githubusercontent.com/ajinabraham/'
                'libsast/master/tests/unit/assets/rules/patterns.yaml')
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    options = {'match_rules': rule_url}
    paths = [files_dir.as_posix()]
    res = libsast.Scanner(options, paths).scan()
    assert res['pattern_matcher']['test_regex_or']


def test_load_invalid_url():
    rule_url = ('https://raw.githubusercontent.com/ajinabraham/'
                'libsast/master/tests/unit/assets/rules')
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    options = {'match_rules': rule_url}
    paths = [files_dir.as_posix()]
    with pytest.raises(libsast.exceptions.RuleDownloadException):
        libsast.Scanner(options, paths).scan()


def test_load_file_invalid_path():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'rules' / 'patterns.yoo'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    with pytest.raises(libsast.exceptions.InvalidRuleError):
        libsast.Scanner(options, paths).scan()


def test_load_file_invalid_yaml():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'invalid' / 'invalid_yaml.yaml'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    with pytest.raises(libsast.exceptions.YamlRuleParseError):
        libsast.Scanner(options, paths).scan()


def test_load_file_invalid_type():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'invalid' / 'invalid_type.yaml'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    with pytest.raises(libsast.exceptions.MatcherNotFoundException):
        libsast.Scanner(options, paths).scan()


def test_load_file_missing_type():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'invalid' / 'missing_type.yaml'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    with pytest.raises(libsast.exceptions.TypeKeyMissingError):
        libsast.Scanner(options, paths).scan()


def test_load_file_missing_pattern():
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rule_file = base_dir / 'assets' / 'invalid' / 'missing_pattern.yaml'
    options = {'match_rules': rule_file.as_posix()}
    paths = [files_dir.as_posix()]
    with pytest.raises(libsast.exceptions.PatternKeyMissingError):
        libsast.Scanner(options, paths).scan()
