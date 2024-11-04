"""Unit Tests - test pattern matchers."""
from .setup_test import scanner

from pathlib import Path


def test_scan_test():
    options = {'match_extensions': ['.test']}
    result = scanner(options).scan()
    assert result['pattern_matcher']['test_regex']


def test_scan_ext():
    options = {'match_extensions': ['.test']}
    result = scanner(options).scan()
    assert result['pattern_matcher'] is not None


def test_scan_ext_not_present():
    options = {'match_extensions': ['.html']}
    result = scanner(options).scan()
    assert result['pattern_matcher'] == {}


def test_ignore_extensions():
    options = {'ignore_extensions': ['.test', '.python']}
    result = scanner(options).scan()
    assert result['pattern_matcher'] == {}
    assert result['choice_matcher'] != {}


def test_ignore_filenames():
    options = {'ignore_filenames': ['test_matcher.test']}
    result = scanner(options).scan()
    assert result['pattern_matcher'] == {}


def test_ignore_paths():
    base_dir = Path(__file__).parents[1]
    files_dir = base_dir / 'assets' / 'files'
    paths = [files_dir.as_posix()]
    options = {'ignore_paths': paths}
    result = scanner(options).scan()
    assert result == {}
