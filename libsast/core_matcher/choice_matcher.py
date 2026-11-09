# -*- coding: utf_8 -*-
"""Choice Matcher."""
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
from libsast.core_matcher.matchers import get_compiled_pattern
from libsast import (
    common,
    exceptions,
)


class ChoiceMatcher:
    def __init__(self, options: dict) -> None:
        self.scan_rules = get_rules(options.get('choice_rules'))
        self.show_progress = options.get('show_progress')
        self.cpu = options.get('cpu_core')
        self.multiprocessing = options.get('multiprocessing')
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

    def _load_formatted_paths(self, unique_paths):
        """Read and format all unique candidate paths in parallel."""
        path_list = list(unique_paths)
        with ThreadPoolExecutor() as io_executor:
            formatted_list = list(io_executor.map(
                self._read_formatted_path, path_list))
        return {
            p: d for p, d in zip(path_list, formatted_list) if d is not None
        }

    def read_file_contents(self, paths: list) -> list:
        """Load file(s) content once and pair with each choice rule."""
        if not paths or not self.scan_rules:
            return []

        alt_path = Path(self.alternative_path) if self.alternative_path else None
        rule_paths = []
        unique_paths = set()
        for rule in self.scan_rules:
            scan_paths = [alt_path] if (
                rule['type'] != 'code' and alt_path) else paths
            rule_paths.append((scan_paths, rule))
            unique_paths.update(scan_paths)

        path_to_data = self._load_formatted_paths(unique_paths)
        return [
            [
                (path_to_data[p], rule)
                for p in scan_paths
                if p in path_to_data
            ]
            for scan_paths, rule in rule_paths
        ]

    def _read_formatted_path(self, sfile):
        """Read and strip comments for a single file once."""
        if not is_file_valid(sfile, self.exts, 5):
            return None
        try:
            return self._format_content(
                sfile.read_text('utf-8', 'ignore'),
                sfile.suffix.lower())
        except Exception as e:
            raise exceptions.RuleProcessingError(
                f'Error reading file: {sfile}') from e

    def regex_scan(self, file_contents: list, rules=None) -> dict:
        """Process regex matches on the file contents."""
        if rules:
            self.scan_rules = get_rules(rules)
        if not (self.scan_rules and file_contents):
            return {}
        self.validate_rules()

        chunksize = max(1, len(file_contents) // ((self.cpu or 1) * 4))
        if self.multiprocessing == 'billiard':
            from billiard import Pool
            with Pool(processes=self.cpu) as pool:
                results = pool.map(
                    self.choice_matcher,
                    file_contents,
                    chunksize=chunksize)
        elif self.multiprocessing == 'thread':
            with ThreadPoolExecutor() as io_executor:
                results = list(io_executor.map(
                    self.choice_matcher,
                    file_contents))
        else:
            with ProcessPoolExecutor(max_workers=self.cpu) as cpu_executor:
                results = list(cpu_executor.map(
                    self.choice_matcher,
                    file_contents,
                    chunksize=chunksize))

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

    def find_choices(self, data, rule):
        """Find Choices using cached compiled patterns."""
        all_matches = set()
        for idx, choice in enumerate(rule['choice']):
            typ = rule['choice_type']
            if typ == 'and':
                if all(get_compiled_pattern(and_regx).search(data)
                       for and_regx in choice[0]):
                    return (all_matches, [idx])
            elif get_compiled_pattern(choice[0]).search(data):
                if typ == 'or':
                    return (all_matches, [idx])
                elif typ == 'all':
                    all_matches.add(choice[1])
        return (all_matches, None)

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

                if all_matches:
                    selection = rule['selection'].format(list(all_matches))
                elif matches:
                    select = rule['choice'][min(matches)][1]
                    selection = rule['selection'].format(select)
                else:
                    selection = rule['selection'].format(rule.get('else', ''))

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
