# -*- coding: utf_8 -*-
"""Choice Matcher."""
import re
from pathlib import Path
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from functools import lru_cache

from libsast.core_matcher.helpers import (
    get_rules,
    is_file_valid,
    strip_comments,
)
from libsast import (
    common,
    exceptions,
)


class ChoiceMatcher:
    def __init__(self, options: dict) -> None:
        self.scan_rules = get_rules(options.get('choice_rules'))
        self.show_progress = options.get('show_progress')
        self.cpu = options.get('cpu_core')
        self.alternative_path = options.get('alternative_path')
        exts = options.get('choice_extensions')
        self.exts = [ext.lower() for ext in exts] if exts else []
        self.findings = {}

    def scan(self, paths: list) -> dict:
        """Scan file(s) or directory per rule."""
        if self.show_progress:
            pbar = common.ProgressBar('Choice Match', len(self.scan_rules))
            self.scan_rules = pbar.progress_loop(self.scan_rules)

        file_contents = self.read_file_contents(paths)
        return self.regex_scan(file_contents)

    def read_file_contents(self, paths: list) -> list:
        """Load file(s) content."""
        if not (self.scan_rules and paths):
            return
        self.validate_rules()
        choice_args = []
        for rule in self.scan_rules:
            scan_paths = paths
            if rule['type'] != 'code' and self.alternative_path:
                # Scan only alternative path
                scan_paths = [Path(self.alternative_path)]
            choice_args.append((scan_paths, rule))
        if not choice_args:
            return []

        # Use ThreadPoolExecutor for file reading
        with ThreadPoolExecutor() as io_executor:
            # Submit file reading tasks and wait for results
            futures = []
            for args_tuple in choice_args:
                future = io_executor.submit(
                    self._read_file_contents, args_tuple)
                futures.append(future)
            return [future.result() for future in futures]

    def regex_scan(self, file_contents) -> list:
        """Process regex matches on the file contents."""
        # Use ProcessPoolExecutor for regex processing
        with ProcessPoolExecutor(max_workers=self.cpu) as cpu_executor:

            results = []
            for content in file_contents:
                # Process Choice Matcher on the file contents
                process_future = cpu_executor.submit(
                    self.choice_matcher, content)
                results.append(process_future.result())

        self.add_finding(results)
        return self.findings

    def validate_rules(self):
        """Validate Rules before scanning."""
        for rule in self.scan_rules:
            if not isinstance(rule, dict):
                raise exceptions.InvalidRuleFormatError(
                    'Choice Matcher Rule format is invalid.')
            required_keys = [
                'id',
                'type',
                'choice_type',
                'selection',
                'choice']
            for key in required_keys:
                if not rule.get(key):
                    raise exceptions.PatternKeyMissingError(
                        f'The rule is missing the key "{key}"')

    def _read_file_contents(self, args_tuple):
        """Read file contents for the given paths and rule."""
        scan_paths, rule = args_tuple
        results = []
        for sfile in scan_paths:
            if not is_file_valid(sfile, self.exts, 5):
                continue
            try:
                data = self._format_content(
                    sfile.read_text('utf-8', 'ignore'),
                    sfile.suffix.lower())
                results.append((data, rule))
            except Exception as e:
                raise exceptions.RuleProcessingError(
                    'Error reading file: {}'.format(sfile)) from e
        return results

    def find_choices(self, data, rule):
        """Find Choices."""
        all_matches = set()
        for idx, choice in enumerate(rule['choice']):
            typ = rule['choice_type']
            if typ == 'and':
                # Return on first and choice
                if all(re.compile(and_regx).search(data) for and_regx in choice[0]):
                    return (all_matches, [idx])
            elif re.compile(choice[0]).search(data):
                if typ == 'or':
                    # Return on first or choice
                    return (all_matches, [idx])
                elif typ == 'all':
                    # Extract all choice(s) from all files
                    all_matches.add(choice[1])
        return (all_matches, None)  # None means no matches found.

    def choice_matcher(self, file_contents):
        """Process regex matches on the file contents."""
        results = []
        for data, rule in file_contents:
            match = self.find_choices(data, rule)
            results.append({
                'rule': rule,
                'matches': match[1] if isinstance(match, tuple) else set(),
                'all_matches': match[0] if isinstance(match, tuple) else match,
            })
        return results

    @staticmethod
    @lru_cache(maxsize=128)
    def _format_content(data, file_suffix):
        return strip_comments(data, file_suffix)

    def add_finding(self, results):
        """Add Choice Findings and generate metadata."""
        for res_list in results:
            if not res_list:
                continue
            for match_dict in res_list:
                rule = match_dict['rule']
                all_matches = match_dict['all_matches']
                matches = match_dict['matches']

                # Determine selection string
                if all_matches:
                    selection = rule['selection'].format(list(all_matches))
                elif matches:
                    select = rule['choice'][min(matches)][1]
                    selection = rule['selection'].format(select)
                else:
                    selection = rule['selection'].format(rule.get('else', ''))

                # Create metadata dictionary
                meta_dict = {
                    'choice': selection,
                    'description': rule['message'],
                    **{key: rule[key] for key in rule if key not in {
                        'choice',
                        'message',
                        'id',
                        'type',
                        'choice_type',
                        'selection',
                        'else'}}}

                self.findings[rule['id']] = meta_dict
