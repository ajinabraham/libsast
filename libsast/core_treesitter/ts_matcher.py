# -*- coding: utf_8 -*-
"""Tree-sitter AST Matcher."""
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from operator import itemgetter

from libsast import (
    common,
    exceptions,
)
from libsast.core_matcher.helpers import (
    get_rules,
    is_file_valid,
)
from libsast.core_treesitter.languages import (
    extract_script_bytes,
    resolve_file_language,
)
from libsast.core_treesitter.matchers import (
    TS_MATCHERS,
    inline_tree_constants,
    parse_tree,
    rule_supports_language,
)


def _prepare_source_bytes(data, is_embedded):
    """Encode file content and extract embedded scripts when needed."""
    raw_bytes = data.encode('utf-8', 'ignore') if isinstance(
        data, str) else bytes(data)
    return extract_script_bytes(raw_bytes) if is_embedded else raw_bytes


def _run_applicable_rules(lang_name, source_bytes, applicable, max_len):
    """Parse AST (and constant-inlined AST) and run applicable rules."""
    raw_tree = parse_tree(lang_name, source_bytes)
    needs_inlining = any(
        r.get('resolve_constants', True) for r in applicable)
    if needs_inlining:
        inlined_tree, shifts = inline_tree_constants(
            lang_name, raw_tree, source_bytes)
    else:
        inlined_tree, shifts = raw_tree, ()
    results = []
    for rule in applicable:
        if rule.get('resolve_constants', True):
            target, active_shifts = inlined_tree, shifts
        else:
            target, active_shifts = raw_tree, ()
        strat = TS_MATCHERS[rule['type']]()
        matches = strat._perform_search(
            target, source_bytes, lang_name, rule, max_len, active_shifts)
        if matches:
            results.append((rule, matches))
    return results


def match_ts_rules_on_file(file_path, data, rules, custom_ext_map=None,
                           max_len=300):
    """Run TreeSitter rules on a single (file_path, content) pair."""
    lang_name, is_embedded = resolve_file_language(file_path, custom_ext_map)
    applicable = [
        r for r in (rules or ())
        if lang_name and rule_supports_language(r, lang_name)
    ]
    if not applicable:
        return []

    source_bytes = _prepare_source_bytes(data, is_embedded)
    if not source_bytes.strip():
        return []

    rule_matches = _run_applicable_rules(
        lang_name, source_bytes, applicable, max_len)
    return [
        {
            'file': file_path.as_posix(),
            'rule': rule,
            'matches': matches,
        }
        for rule, matches in rule_matches
    ]


class TreeSitterMatcher:
    def __init__(self, options: dict) -> None:
        has_ts_rules = bool(options.get('ts_rules'))
        rule_loc = options.get('ts_rules') or options.get('match_rules')
        self.scan_rules = get_rules(rule_loc) if rule_loc else []
        self.show_progress = options.get('show_progress')
        self.cpu = options.get('cpu_core') or 1
        self.multiprocessing = options.get('multiprocessing')
        self.ext_map = options.get('ts_extension_map')
        self.max_size_mb = options.get('ts_max_file_size_mb') or 15
        self.max_match_len = options.get('ts_max_match_length') or 300
        exts = options.get('ts_extensions')
        if not exts and not has_ts_rules:
            exts = options.get('match_extensions')
        self.exts = [ext.lower() for ext in exts] if exts else []
        self.findings = {}

    def scan(self, paths: list) -> dict:
        """Scan file(s) or directory with tree-sitter AST rules."""
        if self.show_progress:
            pbar = common.ProgressBar('Tree-sitter Match', len(paths))
            paths = pbar.progress_loop(paths)
        file_contents = self.read_file_contents(paths)
        return self.ast_scan(file_contents)

    def read_file_contents(self, paths: list) -> list:
        """Load file(s) content."""
        if not paths:
            return []
        files_to_scan = {
            sfile for sfile in paths
            if is_file_valid(sfile, self.exts, self.max_size_mb)
        }
        if not files_to_scan:
            return []
        with ThreadPoolExecutor() as io_executor:
            return list(io_executor.map(
                self._read_file_content, files_to_scan))

    def ast_scan(self, file_contents: list, rules=None) -> dict:
        """Scan file(s) content with tree-sitter rules."""
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
                    self.ts_matcher, file_contents, chunksize=chunksize)
        elif self.multiprocessing == 'thread':
            with ThreadPoolExecutor() as io_executor:
                results = list(io_executor.map(self.ts_matcher, file_contents))
        else:
            with ProcessPoolExecutor(max_workers=self.cpu) as cpu_executor:
                results = list(cpu_executor.map(
                    self.ts_matcher, file_contents, chunksize=chunksize))

        self.add_finding(results)
        return self.findings

    def validate_rules(self):
        """Validate tree-sitter rules before scanning."""
        required_keys = ['type', 'pattern']
        for rule in self.scan_rules:
            if not isinstance(rule, dict):
                raise exceptions.InvalidRuleFormatError(
                    'Tree-sitter Rule format is invalid.')
            missing_keys = [key for key in required_keys if key not in rule]
            if missing_keys:
                mkeys = ', '.join(missing_keys)
                raise exceptions.PatternKeyMissingError(
                    f'The rule is missing the keys: {mkeys}')
            pattern_name = rule['type']
            if pattern_name not in TS_MATCHERS:
                supported = ', '.join(TS_MATCHERS)
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

    def ts_matcher(self, file_data):
        """Run tree-sitter rules against one file."""
        file_path, data = file_data
        try:
            return match_ts_rules_on_file(
                file_path,
                data,
                self.scan_rules,
                self.ext_map,
                self.max_match_len)
        except exceptions.LibsastError:
            raise
        except Exception as e:
            msg = f'Error processing rule for {file_path}: {e}'
            raise exceptions.RuleProcessingError(msg)

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
                    meta = dict(rule.get('metadata', {}) or {})
                    meta['description'] = rule['message']
                    meta['severity'] = rule['severity']
                    self.findings[rule_id]['metadata'] = meta

        sort_key = itemgetter('file_path', 'match_string', 'match_lines')
        for details in self.findings.values():
            details['files'].sort(key=sort_key)
