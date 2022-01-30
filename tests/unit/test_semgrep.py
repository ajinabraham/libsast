"""Unit Tests - test semantic grep patterns."""
from .setup_test import scanner

from libsast import (
    standards,
)


def test_semgrep():
    stds = standards.get_standards()
    result = scanner({}).scan()
    match = result['semantic_grep']['matches']['boto-client-ip']
    assert match
    assert match['files'][0]['match_position']
    assert match['files'][0]['match_lines']
    assert match['files'][0]['file_path']
    assert match['metadata']
    assert match['metadata']['description']
    assert match['metadata']['severity']
    assert match['metadata']['cwe'] == stds['cwe']['cwe-1050']
    assert match['metadata']['owasp-web'] == stds['owasp-web']['a8']
