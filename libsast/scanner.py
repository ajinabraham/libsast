# -*- coding: utf_8 -*-
"""The libsast Scanner module."""
from pathlib import Path

from libsast.core_matcher.pattern_matcher import (
    PatternMatcher,
)
from libsast.core_sgrep.semantic_sgrep import (
    SemanticGrep,
)
from libsast.exceptions import (
    InvalidPathError,
)


class Scanner:
    def __init__(self, options: dict, paths: list) -> None:
        if options:
            self.options = options
        else:
            self.options = {
                'sgrep_rules': None,
                'sgrep_extensions': None,
                'match_rules': None,
                'match_extensions': None,
                'ignore_filenames': None,
                'ignore_extensions': None,
                'ignore_paths': None,
                'show_progress': False,
            }
        if options.get('ignore_extensions'):
            self.ignore_extensions = options.get('ignore_extensions')
        else:
            self.ignore_extensions = []
        if options.get('ignore_filenames'):
            self.ignore_filenames = options.get('ignore_filenames')
        else:
            self.ignore_filenames = []
        if options.get('ignore_paths'):
            self.ignore_paths = options.get('ignore_paths')
        else:
            self.ignore_paths = []
        self.paths = paths

    def scan(self) -> dict:
        """Start Scan."""
        results = {}
        valid_paths = self.get_scan_files(self.paths)
        if not valid_paths:
            return
        if self.options.get('match_rules'):
            results['pattern_matcher'] = PatternMatcher(
                self.options).scan(valid_paths)
        if self.options.get('sgrep_rules'):
            results['semantic_grep'] = SemanticGrep(
                self.options).scan(valid_paths)
        return results

    def get_scan_files(self, paths):
        """Get files valid for scanning."""
        if not isinstance(paths, list):
            raise InvalidPathError('Path should be a list')
        all_files = set()
        for path in paths:
            pobj = Path(path)
            if pobj.is_dir():
                for pfile in pobj.rglob('*'):
                    if self.validate_file(pfile):
                        all_files.add(pfile)
            else:
                if self.validate_file(pobj):
                    all_files.add(pobj)
        return all_files

    def validate_file(self, path):
        """Check if we should scan the file."""
        ignore_paths = any(pp in path.as_posix() for pp in self.ignore_paths)
        ignore_files = path.name in self.ignore_filenames
        ignore_exts = path.suffix.lower() in self.ignore_extensions
        if (ignore_paths or ignore_files or ignore_exts):
            return False
        if not path.exists() or not path.is_file():
            return False
        return True
