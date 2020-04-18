# -*- coding: utf_8 -*-
"""Semantic Grep Core."""
import functools
from argparse import Namespace

from semgrep import sgrep_main

from libsast.logger import init_logger

logger = init_logger(__name__)


def wrap_function(oldfunction, newfunction):
    @functools.wraps(oldfunction)
    def run(*args, **kwargs):
        return newfunction(oldfunction, *args, **kwargs)
    return run


class SemanticGrep:
    def __init__(self, options: dict) -> None:
        self.scan_rules = options.get('sgrep_rules')
        self.findings = {
            'matches': {},
            'errors': [],
        }
        # Monkey patch build_normal_output
        sgrep_main.build_output_json = wrap_function(
            sgrep_main.build_output_json, self._patch)

    def _patch(self, oldfunc, *args, **kwargs):
        return ''

    def scan(self, paths: list) -> dict:
        """Do sgrep scan."""
        args = Namespace(
            autofix=False,
            config=self.scan_rules,
            dangerously_allow_arbitrary_code_execution_from_rules=False,
            dump_ast=False,
            error=False,
            exclude=[],
            exclude_dir=[],
            exclude_tests=False,
            generate_config=False,
            include=[],
            json=True,
            lang=None,
            no_rewrite_rule_ids=False,
            output=None,
            pattern=None,
            precommit=False,
            quiet=False,
            r2c=False,
            strict=False,
            target=paths,
            test=False,
            test_ignore_todo=False,
            validate=False,
            verbose=False,
            version=False)
        self.format_output(sgrep_main.main(args))
        return self.findings

    def format_output(self, sgrep_out):
        """Format sgrep results."""
        self.findings['errors'] = sgrep_out['errors']
        smatches = self.findings['matches']
        for find in sgrep_out['results']:
            file_details = {
                'file_path': find['path'],
                'match_position': (find['start']['col'], find['end']['col']),
                'match_lines': (find['start']['line'], find['end']['line']),
                'match_string': find['extra']['file_lines'],
            }
            rule_id = find['check_id']
            if rule_id in smatches:
                smatches[rule_id]['files'].append(file_details)
            else:
                metdata = find['extra']['metadata']
                metdata['description'] = find['extra']['message']
                metdata['severity'] = find['extra']['severity']
                smatches[rule_id] = {
                    'files': [file_details],
                    'metadata': metdata,
                }
