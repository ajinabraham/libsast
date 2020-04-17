# -*- coding: utf_8 -*-
"""Pattern Macher."""
import copy

from libsast.core_matcher.helpers import get_rules
from libsast.core_matcher.matchers import MatchCommand
from libsast.logger import init_logger

logger = init_logger(__name__)


class PatternMatcher:
    def __init__(self, options: dict) -> None:
        self.matcher = MatchCommand()
        self.scan_rules = get_rules(options.get('match_rules'))
        self.findings = {}

    def scan(self, paths: list) -> dict:
        """Scan file(s) or directory."""
        if not self.scan_rules:
            return
        for file_obj in paths:
            data = file_obj.read_text('utf-8', 'ignore')
            self.pattern_matcher(data, file_obj.as_posix())
        return self.findings

    def pattern_matcher(self, data, file_path):
        """Static Analysis Pattern Matcher."""
        try:
            for rule in self.scan_rules:
                try:
                    rule['type']
                except KeyError:
                    logger.error('match_rule.py should have the '
                                 'match \'type\' defined.')
                    return
                try:
                    rule['pattern']
                except KeyError:
                    logger.error('match_rule.py should have the key'
                                 ' \'match\' defined with the '
                                 'pattern to match')
                    return
                case = rule.get('input_case')
                if case == 'lower':
                    fmt_data = data.lower()
                elif case == 'upper':
                    fmt_data = data.upper()
                else:
                    fmt_data = data
                matches = self.matcher._find_match(rule['type'], fmt_data,
                                                   rule)
                if matches:
                    self.add_finding(file_path, rule, matches)
        except Exception:
            logger.exception('Error in Code Rule Processing')

    def add_finding(self, file_path, rule, matches):
        """Add Code Analysis Findings."""
        for match in matches:
            crule = copy.deepcopy(rule)
            file_details = {
                'file_path': file_path,
                'match_string': match[0],
                'match_position': match[1],
            }
            if rule['id'] in self.findings:
                self.findings[rule['id']]['files'].append(file_details)
            else:
                self.findings[rule['id']] = {
                    'files': [file_details],
                    'metadata': crule,
                }
