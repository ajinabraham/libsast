"""Unit Tests - test standards mapping."""
from pathlib import Path

from libsast import (
    Scanner,
    standards,
)


def test_standards_mapping():
    stds = standards.get_standards()
    base_dir = Path(__file__).parents[1]
    files_dir = base_dir / 'assets' / 'files'
    rules_dir = base_dir / 'assets' / 'rules' / 'pattern_matcher'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    res = Scanner(options, paths).scan()
    match = res['pattern_matcher']['test_regex_multiline_and_metadata']
    assert match
    assert match['metadata']
    assert match['metadata']['cwe'] == stds['cwe']['cwe-1051']
    assert match['metadata']['owasp-mobile'] == stds['owasp-mobile']['m1']
    assert match['metadata']['owasp-web'] == stds['owasp-web']['a10']
    assert match['metadata']['masvs'] == stds['masvs']['storage-3']
    assert match['metadata']['foo'] == 'bar'
