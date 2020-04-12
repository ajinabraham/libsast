"""Unit Tests - test pattern matchers."""
from .setup_test import scanner


def test_matchers():
    result = scanner({}).scan()
    assert result['test_regex']
    assert result['test_regex_and']
    assert result['test_regex_or']
    assert result['test_regex_and_not']
    assert result['test_regex_or']
