"""Unit Tests - test pattern matchers."""
from .setup_test import scanner


def test_matchers():
    result = scanner({}).scan()
    assert result['pattern_matcher']['test_regex']
    assert result['pattern_matcher']['test_regex_and']
    assert result['pattern_matcher']['test_regex_or']
    assert result['pattern_matcher']['test_regex_and_not']
    assert result['pattern_matcher']['test_regex_and_or']
    assert result['pattern_matcher']['test_regex_multiline']
