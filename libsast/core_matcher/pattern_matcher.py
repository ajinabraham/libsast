# -*- coding: utf_8 -*-
"""Pattern Macher."""
from copy import deepcopy

from libsast.core_matcher.helpers import (
    get_rules,
    strip_comments,
    strip_comments2,
)
from libsast.core_matcher import matchers
from libsast import (
    common,
    exceptions,
)


class PatternMatcher:
    def __init__(self, options: dict) -> None:
        self.matcher = matchers.MatchCommand()
        self.scan_rules = get_rules(options.get('match_rules'))
        self.show_progress = options.get('show_progress')
        exts = options.get('match_extensions')
        if exts:
            self.exts = [ext.lower() for ext in exts]
        else:
            self.exts = []
        self.findings = {}

    def scan(self, paths: list) -> dict:
        """Scan file(s) or directory."""
        if not (self.scan_rules and paths):
            return
        self.validate_rules()
        if self.show_progress:
            pbar = common.ProgressBar('Pattern Match', len(paths))
            paths = pbar.progrees_loop(paths)
        for sfile in paths:
            ext = sfile.suffix.lower()
            if self.exts and ext not in self.exts:
                continue
            data = sfile.read_text('utf-8', 'ignore')
            self.pattern_matcher(data, sfile, ext)
        return self.findings

    def validate_rules(self):
        """Validate Rules before scanning."""
        for rule in self.scan_rules:
            if not isinstance(rule, dict):
                raise exceptions.InvalidRuleFormatException(
                    'Pattern Matcher Rule format is invalid.')
            if not rule.get('type'):
                raise exceptions.TypeKeyMissingError(
                    'The rule is missing the key \'type\'')
            if not rule.get('pattern'):
                raise exceptions.PatternKeyMissingError(
                    'The rule is missing the key \'pattern\'')
            all_mts = [m for m in dir(matchers) if m.startswith('R')]
            pattern_name = rule['type']
            if pattern_name not in all_mts:
                supported = ', '.join(all_mts)
                raise exceptions.MatcherNotFoundException(
                    f'Matcher \'{pattern_name}\' is not supported.'
                    f' Available matchers are {supported}',
                )

    def pattern_matcher(self, data, file_path, ext):
        """Static Analysis Pattern Matcher."""
        try:
            for rule in self.scan_rules:
                case = rule.get('input_case')
                if case == 'lower':
                    tmp_data = data.lower()
                elif case == 'upper':
                    tmp_data = data.upper()
                else:
                    tmp_data = data
                if ext in ('.html', '.xml'):
                    fmt_data = strip_comments2(tmp_data)
                else:
                    fmt_data = strip_comments(tmp_data)
                matches = self.matcher._find_match(
                    rule['type'],
                    fmt_data,
                    rule)
                if matches:
                    self.add_finding(file_path, rule, matches)
        except Exception:
            raise exceptions.RuleProcessingException('Rule processing error.')

    def add_finding(self, file_path, rule, matches):
        """Add Code Analysis Findings."""
        for match in matches:
            crule = deepcopy(rule)
            file_details = {
                'file_path': file_path.as_posix(),
                'match_string': match[0],
                'match_position': match[1],
                'match_lines': match[2],
            }
            if rule['id'] in self.findings:
                self.findings[rule['id']]['files'].append(file_details)
            else:
                self.findings[rule['id']] = {
                    'files': [file_details],
                    'metadata': crule,
                }
