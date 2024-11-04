# -*- coding: utf_8 -*-
"""Optimized Algorithms for Pattern Matching with Caching."""
import re
from abc import ABC, abstractmethod
from functools import lru_cache

from libsast.core_matcher.helpers import get_match_lines


def get_pos(match):
    """Adjust zero index in match span."""
    start, end = match.span()
    return (1 if start == 0 else start, end)


# Cache compiled regex patterns
@lru_cache(maxsize=128)
def get_compiled_pattern(pattern):
    """Compile and cache regex patterns."""
    return re.compile(pattern)


class MatchCommand:
    def __init__(self):
        self.patterns = {}

    def _find_match(self, pattern_name, content, rule):
        pattern_class = self.patterns.get(pattern_name) or globals()[pattern_name]()
        self.patterns.setdefault(pattern_name, pattern_class)
        case = rule.get('input_case')
        if case == 'lower':
            content = content.lower()
        elif case == 'upper':
            content = content.upper()
        return pattern_class._perform_search(content, rule)


class MatchStrategy(ABC):
    @abstractmethod
    def _perform_search(self, content, rule):
        """Search for instances of a pattern match in content."""


class Regex(MatchStrategy):
    def _perform_search(self, content, rule):
        pattern = get_compiled_pattern(rule['pattern'])
        return self._find_matches(content, pattern)

    @staticmethod
    def _find_matches(content, pattern):
        """Helper to find all matches in content and extract details."""
        matches = set()
        for match in pattern.finditer(content):
            if match.group():
                match_pos = get_pos(match)
                match_lines = get_match_lines(content, match_pos)
                matches.add((match.group(), match_pos, match_lines))
        return matches


class RegexAnd(MatchStrategy):
    def _perform_search(self, content, rule):
        patterns = rule['pattern'] if isinstance(
            rule['pattern'], list) else [rule['pattern']]
        all_matches = set()
        for regex in patterns:
            pattern = get_compiled_pattern(regex)
            matches = Regex._find_matches(content, pattern)
            if not matches:
                return False
            all_matches.update(matches)
        return all_matches


class RegexOr(MatchStrategy):
    def _perform_search(self, content, rule):
        patterns = rule['pattern'] if isinstance(
            rule['pattern'], list) else [rule['pattern']]
        matches = set()
        for regex in patterns:
            pattern = get_compiled_pattern(regex)
            matches.update(Regex._find_matches(content, pattern))
        return matches


class RegexAndNot(MatchStrategy):
    def _perform_search(self, content, rule):
        present_pattern, not_pattern = rule['pattern']
        not_found = get_compiled_pattern(not_pattern).search(content) is None
        if not not_found:
            return False
        present_matches = Regex._find_matches(
            content, get_compiled_pattern(present_pattern))
        return present_matches if present_matches else False


class RegexAndOr(MatchStrategy):
    def _perform_search(self, content, rule):
        and_pattern, or_patterns = rule['pattern']
        and_matches = Regex._find_matches(content, get_compiled_pattern(and_pattern))
        or_matches = set()
        for regex in or_patterns:
            or_pattern = get_compiled_pattern(regex)
            or_matches = Regex._find_matches(content, or_pattern)
            if or_matches:
                break
        if and_matches and or_matches:
            return and_matches.union(or_matches)
        return False
