"""Unit Tests - test pattern matchers."""
from .setup_test import scanner


def test_pattern_matcher():
    result = scanner({}).scan()
    assert result['pattern_matcher']['test_regex']
    assert result['pattern_matcher']['test_regex_and']
    assert result['pattern_matcher']['test_regex_or']
    assert result['pattern_matcher']['test_regex_and_not']
    assert result['pattern_matcher']['test_regex_and_or']
    assert result['pattern_matcher']['test_regex_multiline_and_metadata']
    assert result['pattern_matcher']['test_regex_case']


def test_choice_matcher():
    result = scanner({}).scan()
    assert result['choice_matcher']['rule1']
    assert result['choice_matcher']['rule2']
    assert result['choice_matcher']['rule3']
