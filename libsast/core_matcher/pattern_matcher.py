# -*- coding: utf_8 -*-
"""Pattern Matcher."""
from operator import itemgetter
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
        self.cpu = options.get('cpu_core')
        exts = options.get('match_extensions')
        self.exts = [ext.lower() for ext in exts] if exts else []
        self.findings = {}

    def scan(self, paths: list) -> dict:
        """Scan file(s) or directory."""
        if self.show_progress:
            pbar = common.ProgressBar('Pattern Match', len(paths))
            paths = pbar.progress_loop(paths)

        file_contents = self.read_file_contents(paths)
        return self.regex_scan(file_contents)

    def read_file_contents(self, paths: list) -> list:
        """Load file(s) content."""
        if not (self.scan_rules and paths):
            return
        self.validate_rules()

        # Filter files by extension and size, prepare list for processing
        files_to_scan = {
            sfile for sfile in paths
            if is_file_valid(sfile, self.exts, 5)
        }
        if not files_to_scan:
            return []

        # Use a ThreadPool for file reading
        with ThreadPoolExecutor() as io_executor:

            # Read all files
            file_contents = list(io_executor.map(
                self._read_file_content, files_to_scan))
            return file_contents

    def regex_scan(self, file_contents: list) -> dict:
        """Scan file(s) content."""
        # Use a ProcessPool for CPU-bound regex
        with ProcessPoolExecutor(max_workers=self.cpu) as cpu_executor:

            # Run regex on file data
            results = cpu_executor.map(
                self.pattern_matcher,
                file_contents,
            )

        # Compile findings
        self.add_finding(results)
        return self.findings

    def validate_rules(self):
        """Validate Rules before scanning."""
        available_matchers = {m for m in dir(matchers) if m.startswith('R')}
        required_keys = ['type', 'pattern']

        for rule in self.scan_rules:
            if not isinstance(rule, dict):
                raise exceptions.InvalidRuleFormatError(
                    'Pattern Matcher Rule format is invalid.')

            # Check for missing required keys
            missing_keys = [key for key in required_keys if key not in rule]
            if missing_keys:
                mkeys = ', '.join(missing_keys)
                raise exceptions.PatternKeyMissingError(
                    f'The rule is missing the keys: {mkeys}')

            pattern_name = rule['type']
            if pattern_name not in available_matchers:
                supported = ', '.join(available_matchers)
                raise exceptions.MatcherNotFoundError(
                    f'Matcher {pattern_name} is not supported.'
                    f' Available matchers are {supported}.')

    @staticmethod
    def _read_file_content(file_path):
        """Read file content with encoding handling."""
        try:
            return file_path, file_path.read_text('utf-8', 'ignore')
        except Exception as e:
            print(f'Error reading {file_path}: {e}')
            return file_path, ''

    def pattern_matcher(self, file_data):
        """Static Analysis Pattern Matcher."""
        file_path, data = file_data
        results = []
        try:
            fmt_data = self._format_content(data, file_path.suffix.lower())
            for rule in self.scan_rules:
                matches = self.matcher._find_match(rule['type'], fmt_data, rule)
                if matches:
                    results.append({
                        'file': file_path.as_posix(),
                        'rule': rule,
                        'matches': matches,
                    })
        except Exception as e:
            msg = f'Error processing rule for {file_path}: {e}'
            raise exceptions.RuleProcessingError(msg)
        return results

    @staticmethod
    @lru_cache(maxsize=128)
    def _format_content(data, file_suffix):
        return strip_comments(data, file_suffix)

    def add_finding(self, results):
        """Add Code Analysis Findings."""
        for res_list in results:
            if not res_list:
                continue
            for match_dict in res_list:
                rule = match_dict['rule']
                rule_id = rule['id']
                files = self.findings.setdefault(
                    rule_id, {'files': [], 'metadata': {}})['files']

                for match in match_dict['matches']:
                    file_details = {
                        'file_path': match_dict['file'],
                        'match_string': match[0],
                        'match_position': match[1],
                        'match_lines': match[2],
                    }
                    files.append(file_details)

                if not self.findings[rule_id]['metadata']:
                    meta = rule.get('metadata', {})
                    # message & severity are mandatory
                    meta['description'] = rule['message']
                    meta['severity'] = rule['severity']
                    self.findings[rule_id]['metadata'] = meta

                # Sort files by specified criteria
                self.findings[rule_id]['files'].sort(
                    key=itemgetter('file_path', 'match_string', 'match_lines'))
