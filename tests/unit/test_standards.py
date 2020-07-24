"""Unit Tests - test standards mapping."""
from pathlib import Path

import libsast


def test_standards_mapping():
    a10 = 'A10: Insufficient Logging & Monitoring'
    m1 = 'M1: Improper Platform Usage'
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    rules_dir = base_dir / 'assets' / 'rules' / 'pattern_matcher'
    options = {'match_rules': rules_dir.as_posix()}
    paths = [files_dir.as_posix()]
    res = libsast.Scanner(options, paths).scan()
    match = res['pattern_matcher']['test_regex_multiline']
    assert match
    assert match['metadata']
    assert match['metadata']['cwe'] == 'cwe-1002'
    assert match['metadata']['owasp-mobile'] == m1
    assert match['metadata']['owasp-web'] == a10
    assert match['metadata']['masvs'] == 'MSTG-STORAGE-3'
