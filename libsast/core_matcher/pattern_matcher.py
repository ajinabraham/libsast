# -*- coding: utf_8 -*-
"""Pattern Macher."""
from copy import deepcopy
from operator import itemgetter
from multiprocessing import (
    Pool,
)

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
        files_to_scan = set()
        for sfile in paths:
            if self.exts and sfile.suffix.lower() not in self.exts:
                continue
            if sfile.stat().st_size / 1000 / 1000 > 5:
                # Skip scanning files greater than 5 MB
                print(f'Skipping large file {sfile.as_posix()}')
                continue
            files_to_scan.add(sfile)
        # Multiprocess Pool
        with Pool(common.get_worker_count()) as pool:
            results = pool.map(
                self.pattern_matcher,
                files_to_scan,
                chunksize=1)
        self.add_finding(results)
        return self.findings

    def validate_rules(self):
        """Validate Rules before scanning."""
        for rule in self.scan_rules:
            if not isinstance(rule, dict):
                raise exceptions.InvalidRuleFormatError(
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
                raise exceptions.MatcherNotFoundError(
                    f'Matcher \'{pattern_name}\' is not supported.'
                    f' Available matchers are {supported}',
                )

    def pattern_matcher(self, file_path):
        """Static Analysis Pattern Matcher."""
        results = []
        try:
            data = file_path.read_text('utf-8', 'ignore')
            for rule in self.scan_rules:
                case = rule.get('input_case')
                if case == 'lower':
                    tmp_data = data.lower()
                elif case == 'upper':
                    tmp_data = data.upper()
                else:
                    tmp_data = data
                if file_path.suffix.lower() in ('.html', '.xml'):
                    fmt_data = strip_comments2(tmp_data)
                else:
                    fmt_data = strip_comments(tmp_data)
                matches = self.matcher._find_match(
                    rule['type'],
                    fmt_data,
                    rule)
                if matches:
                    results.append({
                        'file': file_path.as_posix(),
                        'rule': rule,
                        'matches': matches,
                    })
        except Exception:
            raise exceptions.RuleProcessingError('Rule processing error.')
        return results

    def add_finding(self, results):
        """Add Code Analysis Findings."""
        for res_list in results:
            if not res_list:
                continue
            for match_dict in res_list:
                rule = match_dict['rule']
                for match in match_dict['matches']:
                    crule = deepcopy(rule)
                    file_details = {
                        'file_path': match_dict['file'],
                        'match_string': match[0],
                        'match_position': match[1],
                        'match_lines': match[2],
                    }
                    if rule['id'] in self.findings:
                        self.findings[rule['id']]['files'].append(file_details)
                    else:
                        metadata = crule.get('metadata', {})
                        metadata['description'] = crule['message']
                        metadata['severity'] = crule['severity']
                        self.findings[rule['id']] = {
                            'files': [file_details],
                            'metadata': metadata,
                        }
                self.findings[rule['id']]['files'] = sorted(
                    self.findings[rule['id']]['files'],
                    key=itemgetter('file_path', 'match_string', 'match_lines'))
