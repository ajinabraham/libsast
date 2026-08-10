"""Unit Tests - test semantic grep patterns."""
from .setup_test import scanner

from libsast import (
    standards,
)


def test_semgrep():
    result = scanner({}).scan()
    assert result['semantic_grep']['errors'] == []
    match = result['semantic_grep']['matches']['boto-client-ip']
    assert match
    file_hit = match['files'][0]
    assert file_hit['match_position'] == (24, 31)
    assert file_hit['match_lines'] == (4, 4)
    assert file_hit['file_path'].endswith('example_file.py')
    assert file_hit['match_string'] == "c = boto3.client(host='8.8.8.8')"


def test_semgrep_metadata():
    stds = standards.get_standards()
    match = scanner({}).scan()['semantic_grep']['matches']['boto-client-ip']
    assert match['metadata']['description']
    assert match['metadata']['severity']
    assert match['metadata']['cwe'] == stds['cwe']['cwe-1050']
    assert match['metadata']['owasp-web'] == stds['owasp-web']['a8']
