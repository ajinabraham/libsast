"""Test Setup."""
from pathlib import Path

import libsast


def scanner(options):
    base_dir = Path(__file__).parents[1]
    files_dir = base_dir / 'assets' / 'files'
    paths = [files_dir.as_posix()]
    rules_dir = base_dir / 'assets' / 'rules' / 'pattern_matcher'
    sgrep_dir = base_dir / 'assets' / 'rules' / 'semantic_grep'
    options['match_rules'] = rules_dir.as_posix()
    options['sgrep_rules'] = sgrep_dir.as_posix()
    return libsast.Scanner(options, paths)
