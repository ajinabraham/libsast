"""Unit Tests - test semantic grep patterns."""
from .setup_test import scanner


def test_semgrep():
    result = scanner({}).scan()
    match = result['semantic_grep']['matches']['boto-client-ip']
    assert match
    assert match['files'][0]['match_position']
    assert match['files'][0]['match_lines']
    assert match['files'][0]['file_path']
    assert match['metadata']
    assert match['metadata']['description']
    assert match['metadata']['severity']
    assert match['metadata']['owasp']
