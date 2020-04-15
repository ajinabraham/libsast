# -*- coding: utf_8 -*-
"""Pattern Macher."""
import copy
import os
from pathlib import Path

from libsast.core_matcher.helpers import get_rules
from libsast.core_matcher.matchers import MatchCommand
from libsast.logger import init_logger

logger = init_logger(__name__)


class PatternMatcher:
    def __init__(self, options: dict) -> None:
        self.matcher = MatchCommand()
        self.scan_rules = get_rules(options.get('match_rules'))
        if options.get('match_extensions'):
            self.exts = options.get('match_extensions')
        else:
            self.exts = []
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
        self.findings = {}

    def scan(self, paths: list) -> dict:
        """Scan file(s) or directory."""
        if not self.scan_rules:
            return
        if not isinstance(paths, list):
            logger.error('A list of path is expected')
            return
        all_files = set()
        for path in paths:
            pobj = Path(path)
            if pobj.is_dir():
                for root, _, files in os.walk(path):
                    for filename in files:
                        pfile = Path(os.path.join(root, filename))
                        all_files.add(pfile)
            else:
                all_files.add(pobj)
        for file_obj in all_files:
            if not self.validate_file(file_obj):
                continue
            data = file_obj.read_text('utf-8', 'ignore')
            self.pattern_matcher(data, file_obj.as_posix())
        return self.findings

    def validate_file(self, path):
        """Check if we should scan the file."""
        ignore_paths = any(pp in path.as_posix() for pp in self.ignore_paths)
        ignore_files = path.name in self.ignore_filenames
        ignore_exts = path.suffix.lower() in self.ignore_extensions
        if (ignore_paths or ignore_files or ignore_exts):
            return False
        if not self.exts:
            pass
        elif not path.suffix.lower() in self.exts:
            return False
        if not path.exists() or not path.is_file():
            return False
        return True

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
            details = {
                'file_path': file_path,
                'match_string': match[0],
                'match_position': match[1],
            }
            if rule['id'] in self.findings:
                self.findings[rule['id']]['details'].append(details)
            else:
                self.findings[rule['id']] = {
                    'details': [details],
                    'rule': crule,
                }
