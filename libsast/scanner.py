# -*- coding: utf_8 -*-
"""The libsast Scanner module."""
from pathlib import Path
from fnmatch import fnmatch

from libsast.common import get_worker_count
from libsast.core_matcher.pattern_matcher import PatternMatcher
from libsast.core_matcher.choice_matcher import ChoiceMatcher
from libsast.core_sgrep.semantic_sgrep import SemanticGrep
from libsast.exceptions import InvalidPathError


class Scanner:
    def __init__(self, options: dict, paths: list) -> None:
        # Set options with default values where missing
        self.options = {
            'sgrep_rules': None,
            'sgrep_extensions': None,
            'match_rules': None,
            'match_extensions': None,
            'choice_rules': None,
            'choice_extensions': None,
            'alternative_path': None,
            'ignore_filenames': [],
            'ignore_extensions': [],
            'ignore_paths': [],
            'show_progress': False,
            'cpu_core': 1,
            # Overwrite with options from invocation
            **(options or {}),
        }

        # Cache frequently used settings
        if options.get('ignore_extensions'):
            self.ignore_extensions = set(options.get('ignore_extensions'))
        else:
            self.ignore_extensions = set()
        if options.get('ignore_filenames'):
            self.ignore_filenames = set(options.get('ignore_filenames'))
        else:
            self.ignore_filenames = set()
        if options.get('ignore_paths'):
            self.ignore_paths = {
                Path(p).as_posix() for p in self.options['ignore_paths']}
        else:
            self.ignore_paths = set()
        if options.get('cpu_core') and isinstance(options['cpu_core'], int):
            self.options['cpu_core'] = options['cpu_core']
        else:
            self.options['cpu_core'] = get_worker_count()
        self.paths = paths

    def scan(self) -> dict:
        """Start Scan."""
        results = {}
        valid_paths = self.get_scan_files(self.paths)

        if not valid_paths:
            return {}

        if self.options['match_rules']:
            results['pattern_matcher'] = PatternMatcher(self.options).scan(valid_paths)
        if self.options['choice_rules']:
            results['choice_matcher'] = ChoiceMatcher(self.options).scan(valid_paths)
        if self.options['sgrep_rules']:
            results['semantic_grep'] = SemanticGrep(self.options).scan(valid_paths)

        return results

    def get_scan_files(self, paths):
        """Get files valid for scanning."""
        if not isinstance(paths, list):
            raise InvalidPathError('Path should be a list')

        all_files = set()
        for path in paths:
            pobj = Path(path)
            if pobj.is_dir():
                all_files.update({
                    pfile
                    for pfile in pobj.rglob('*')
                    if self.validate_file(pfile)
                })
            elif pobj.is_file() and self.validate_file(pobj):
                all_files.add(pobj)

        return all_files

    def validate_file(self, path):
        """Check if we should scan the file."""
        # Early exit if the path is not a file or does not exist
        if not path.exists() or not path.is_file():
            return False

        # Validate against ignore conditions
        ignore_conditions = any([
            any(pp in path.as_posix() for pp in self.ignore_paths),
            any(fnmatch(path.name, pattern) for pattern in self.ignore_filenames),
            path.suffix.lower() in self.ignore_extensions,
        ])

        return not ignore_conditions
