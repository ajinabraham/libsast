#!/usr/bin/env python
# -*- coding: utf_8 -*-
"""The libsast Scanner module."""

from libsast.core_matcher.pattern_matcher import (
    PatternMatcher,
)


class Scanner:
    def __init__(self, options, paths):
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

    def scan(self):
        """Start Scan."""
        return PatternMatcher(self.options).scan(self.paths)
