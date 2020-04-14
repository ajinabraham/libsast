# -*- coding: utf_8 -*-
"""The libsast Scanner module."""

from libsast.core_matcher.pattern_matcher import (
    PatternMatcher,
)
from libsast.core_sgrep.semantic_sgrep import (
    SemanticGrep,
)


class Scanner:
    def __init__(self, options: dict, paths: list) -> None:
        if options:
            self.options = options
        else:
            self.options = {
                'sgrep_rules': None,
                'sgrep_binary': None,
                'sgrep_extensions': None,
                'match_rules': None,
                'match_extensions': None,
                'ignore_filenames': None,
                'ignore_extensions': None,
                'ignore_paths': None,
            }
        self.paths = paths

    def scan(self) -> dict:
        """Start Scan."""
        results = {}
        if self.options.get('match_rules'):
            results['pattern_matcher'] = PatternMatcher(
                self.options).scan(self.paths)
        if self.options.get('sgrep_rules'):
            results['semantic_grep'] = SemanticGrep(
                self.options).scan(self.paths)
        return results
