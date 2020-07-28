# -*- coding: utf_8 -*-
"""Alogrithms for Matching Pattern."""
import re
from abc import ABC, abstractclassmethod


def get_match_lines(content, pos):
    """Get Match lines from position."""
    start_line = 0
    filepos = 0
    skip = False
    for idx, line in enumerate(content.split('\n'), 1):
        filepos += len(line) + 1
        if filepos >= pos[0] and filepos >= pos[1] and not skip:
            # Match is on the same line
            return (idx, idx)
        elif filepos >= pos[0] and not skip:
            # Multiline match, find start line
            skip = True
            start_line = idx
        if filepos >= pos[1] and skip:
            # Multiline march, find end line
            return (start_line, idx)


class MatchCommand:

    def __init__(self):
        self.patterns = {}

    def _find_match(self, pattern_name, content, rule):
        if pattern_name not in self.patterns:
            pattern_class = globals()[pattern_name]
            self.patterns[pattern_name] = pattern_class()
        return self.patterns[pattern_name]._perform_search(content, rule)


class MatchStrategy(ABC):

    @abstractclassmethod
    def _perform_search(self, content, rule):
        """Search for instance of match in content."""


class Regex(MatchStrategy):
    def _perform_search(self, content, rule):
        matches = set()
        for match in re.compile(rule['pattern']).finditer(content):
            if match.group():
                match_pos = match.span()
                match_lines = get_match_lines(content, match_pos)
                matches.add((match.group(), match_pos, match_lines))
        return matches


class RegexAnd(MatchStrategy):
    def _perform_search(self, content, rule):
        if isinstance(rule['pattern'], str):
            return Regex().perform_search(content, rule)
        matches = set()
        for regex in rule['pattern']:
            empty_iter_detected = True
            for match in re.compile(regex).finditer(content):
                empty_iter_detected = False
                match_pos = match.span()
                match_lines = get_match_lines(content, match_pos)
                matches.add((match.group(), match_pos, match_lines))
            if empty_iter_detected:
                return False
        return matches


class RegexOr(MatchStrategy):
    def _perform_search(self, content, rule):
        if isinstance(rule['pattern'], str):
            return Regex().perform_search(content, rule)
        matches = set()
        for regex in rule['pattern']:
            for match in re.compile(regex).finditer(content):
                if match.group():
                    match_pos = match.span()
                    match_lines = get_match_lines(content, match_pos)
                    matches.add((match.group(), match_pos, match_lines))
        return matches


class RegexAndNot(MatchStrategy):
    def _perform_search(self, content, rule):
        matches = set()
        regex_present = re.compile(rule['pattern'][0]).finditer(content)
        regex_not = re.compile(rule['pattern'][1]).finditer(content)
        for match in regex_not:
            if match.group():
                return False
        for match in regex_present:
            if match.group():
                match_pos = match.span()
                match_lines = get_match_lines(content, match_pos)
                matches.add((match.group(), match_pos, match_lines))
        return matches


class RegexAndOr(MatchStrategy):
    def _perform_search(self, content, rule):
        matches = set()
        or_matches = set()
        or_list = rule['pattern'][1]
        break_parent_loop = False
        for regex in or_list:
            for match in re.compile(regex).finditer(content):
                if match.group():
                    match_pos = match.span()
                    match_lines = get_match_lines(content, match_pos)
                    or_matches.add((match.group(), match_pos, match_lines))
                    break_parent_loop = True
                    break
            if break_parent_loop:
                break
        for match in re.compile(rule['pattern'][0]).finditer(content):
            if match.group():
                match_pos = match.span()
                match_lines = get_match_lines(content, match_pos)
                matches.add((match.group(), match_pos, match_lines))
        if not (matches and or_matches):
            return False
        matches.update(or_matches)
        return matches
