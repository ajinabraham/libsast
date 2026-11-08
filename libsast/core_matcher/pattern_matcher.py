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
from libsast.core_treesitter.matchers import TS_MATCHERS
from libsast.core_treesitter.ts_matcher import match_ts_rules_on_file
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
        self.multiprocessing = options.get('multiprocessing')
        self.ts_ext_map = options.get('ts_extension_map')
        self.ts_max_match_len = options.get('ts_max_match_length') or 300
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
        if not paths:
            return []

        files_to_scan = {
            sfile for sfile in paths
            if is_file_valid(sfile, self.exts, 5)
        }
        if not files_to_scan:
            return []

        with ThreadPoolExecutor() as io_executor:
            file_contents = list(io_executor.map(
                self._read_file_content, files_to_scan))
            return file_contents

    def regex_scan(self, file_contents: list, rules=None) -> dict:
        """Scan file(s) content."""
        if rules:
            self.scan_rules = get_rules(rules)
        if not (self.scan_rules and file_contents):
            return {}
        self.validate_rules()

        chunksize = max(1, len(file_contents) // ((self.cpu or 1) * 4))
        if self.multiprocessing == 'billiard':
            from billiard import Pool
            with Pool(processes=self.cpu) as cpu_executor:
                results = cpu_executor.map(
                    self.pattern_matcher,
                    file_contents,
                    chunksize=chunksize,
                )
        elif self.multiprocessing == 'thread':
            with ThreadPoolExecutor() as io_executor:
                results = io_executor.map(
                    self.pattern_matcher,
                    file_contents,
                )
        else:
            with ProcessPoolExecutor(max_workers=self.cpu) as cpu_executor:
                results = cpu_executor.map(
                    self.pattern_matcher,
                    file_contents,
                    chunksize=chunksize,
                )

        self.add_finding(results)
        return self.findings

    def validate_rules(self):
        """Validate Rules before scanning."""
        regex_matchers = {m for m in dir(matchers) if m.startswith('R')}
        available_matchers = regex_matchers | set(TS_MATCHERS)
        required_keys = ['type', 'pattern']

        for rule in self.scan_rules:
            if not isinstance(rule, dict):
                raise exceptions.InvalidRuleFormatError(
                    'Pattern Matcher Rule format is invalid.')

            missing_keys = [key for key in required_keys if key not in rule]
            if missing_keys:
                mkeys = ', '.join(missing_keys)
                raise exceptions.PatternKeyMissingError(
                    f'The rule is missing the keys: {mkeys}')

            pattern_name = rule['type']
            if pattern_name not in available_matchers:
                supported = ', '.join(sorted(available_matchers))
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

    def _match_regex_rules(self, file_path, data, regex_rules):
        """Run regex rules against formatted file content."""
        if not regex_rules:
            return []
        results = []
        fmt_data = self._format_content(data, file_path.suffix.lower())
        case_cache = {'exact': fmt_data, None: fmt_data}
        for rule in regex_rules:
            case = rule.get('input_case')
            if case not in case_cache:
                if case == 'lower':
                    case_cache[case] = fmt_data.lower()
                elif case == 'upper':
                    case_cache[case] = fmt_data.upper()
                else:
                    case_cache[case] = fmt_data
            rule_view = (
                {**rule, 'input_case': 'exact'} if case in ('lower', 'upper')
                else rule
            )
            matches = self.matcher._find_match(
                rule['type'], case_cache[case], rule_view)
            if matches:
                results.append({
                    'file': file_path.as_posix(),
                    'rule': rule,
                    'matches': matches,
                })
        return results

    def pattern_matcher(self, file_data):
        """Static Analysis Pattern Matcher."""
        file_path, data = file_data
        try:
            regex_rules = [
                r for r in self.scan_rules if r['type'] not in TS_MATCHERS
            ]
            ts_rules = [
                r for r in self.scan_rules if r['type'] in TS_MATCHERS
            ]
            results = self._match_regex_rules(file_path, data, regex_rules)
            if ts_rules:
                results.extend(match_ts_rules_on_file(
                    file_path,
                    data,
                    ts_rules,
                    self.ts_ext_map,
                    self.ts_max_match_len))
            return results
        except exceptions.LibsastError:
            raise
        except Exception as e:
            msg = f'Error processing rule for {file_path}: {e}'
            raise exceptions.RuleProcessingError(msg)

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
                    meta['description'] = rule['message']
                    meta['severity'] = rule['severity']
                    self.findings[rule_id]['metadata'] = meta

        sort_key = itemgetter('file_path', 'match_string', 'match_lines')
        for details in self.findings.values():
            details['files'].sort(key=sort_key)
