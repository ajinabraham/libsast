# -*- coding: utf_8 -*-
"""Semantic Grep Core."""
from libsast.core_sgrep.helpers import invoke_semgrep
from libsast import common


class SemanticGrep:
    def __init__(self, options: dict) -> None:
        self.scan_rules = options.get('sgrep_rules')
        self.show_progress = options.get('show_progress')
        exts = options.get('sgrep_extensions')
        if exts:
            self.exts = [ext.lower() for ext in exts]
        else:
            self.exts = []
        self.findings = {
            'matches': {},
            'errors': [],
        }

    def scan(self, paths: list) -> dict:
        """Do sgrep scan."""
        if self.exts:
            filtered = []
            for sfile in paths:
                if sfile.suffix.lower() in self.exts:
                    filtered.append(sfile)
            if filtered:
                paths = filtered
        if self.show_progress:
            pbar = common.ProgressBar('Semantic Grep', len(paths))
            sgrep_out = pbar.progress_function(
                invoke_semgrep,
                (paths, self.scan_rules))
        else:
            sgrep_out = invoke_semgrep(paths, self.scan_rules)
        self.format_output(sgrep_out)
        return self.findings

    def format_output(self, results):
        """Format sgrep results."""
        self.findings['errors'] = results['errors']
        smatches = self.findings['matches']
        for find in results['results']:
            file_details = {
                'file_path': find['path'],
                'match_position': (find['start']['col'], find['end']['col']),
                'match_lines': (find['start']['line'], find['end']['line']),
                'match_string': find['extra']['lines'],
            }
            rule_id = find['check_id'].rsplit('.', 1)[1]
            if rule_id in smatches:
                smatches[rule_id]['files'].append(file_details)
            else:
                metadata = find['extra']['metadata']
                metadata['description'] = find['extra']['message']
                metadata['severity'] = find['extra']['severity']
                smatches[rule_id] = {
                    'files': [file_details],
                    'metadata': metadata,
                }
