"""Test Setup."""
from pathlib import Path

import libsast


def scanner(options):
    base_dir = Path(__file__).parents[0]
    files_dir = base_dir / 'assets' / 'files'
    paths = [files_dir.as_posix()]
    rules_dir = base_dir / 'assets' / 'rules'
    options['match_rules'] = rules_dir.as_posix()
    return libsast.Scanner(options, paths)
