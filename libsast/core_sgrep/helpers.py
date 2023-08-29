# -*- coding: utf_8 -*-
"""Semantic Grep Helpers."""
import json
import logging
import platform
import multiprocessing


def invoke_semgrep(paths, scan_rules, **kwargs):
    """Call Semgrep."""
    if platform.system() == 'Windows':
        return None
    from semgrep import semgrep_main
    from semgrep.state import get_state
    from semgrep.constants import OutputFormat
    from semgrep.output import OutputHandler, OutputSettings
    try:
        cpu_count = multiprocessing.cpu_count()
    except NotImplementedError:
        cpu_count = 1  # CPU count is not implemented on Windows
    # Semgrep output formatting
    state = get_state()
    state.terminal.configure(
        verbose=False,
        debug=False,
        quiet=True,
        force_color=False,
    )
    logging.getLogger('semgrep').propagate = False
    output_settings = OutputSettings(
        output_format=OutputFormat.JSON,
        output_destination=None,
        output_per_finding_max_lines_limit=None,
        output_per_line_max_chars_limit=None,
        error_on_findings=False,
        verbose_errors=False,
        strict=False,
        timeout_threshold=3,
    )
    output_handler = OutputHandler(output_settings)
    (
        filtered_matches_by_rule,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = semgrep_main.main(
        output_handler=output_handler,
        target=[pt.as_posix() for pt in paths],
        jobs=cpu_count,
        pattern=None,
        lang=None,
        configs=[scan_rules],
        timeout=5,
        timeout_threshold=3,
        **kwargs,
    )
    output_handler.rule_matches = [
        m for ms in filtered_matches_by_rule.values() for m in ms
    ]
    return json.loads(output_handler._build_output())
