# -*- coding: utf_8 -*-
"""Semantic Grep Helpers."""
import multiprocessing

from semgrep import semgrep_main

try:
    CPU_COUNT = multiprocessing.cpu_count()
except NotImplementedError:
    CPU_COUNT = 1  # CPU count is not implemented on Windows


def call_semgrep(paths, scan_rules):
    """Call Semgrep."""
    return semgrep_main.main(
        target=paths,
        pattern=None,
        lang=None,
        config=scan_rules,
        generate_config=False,
        no_rewrite_rule_ids=False,
        jobs=CPU_COUNT,
        include=[],
        include_dir=[],
        exclude=[],
        exclude_dir=[],
        exclude_tests=False,
        json_format=True,
        sarif=False,
        output_destination=None,
        quiet=True,
        strict=False,
        exit_on_error=False,
        autofix=False,
        dangerously_allow_arbitrary_code_execution_from_rules=False)
