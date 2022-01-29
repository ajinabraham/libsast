# -*- coding: utf_8 -*-
"""Semantic Grep Helpers."""
import json
import platform
import multiprocessing


def invoke_semgrep(paths, scan_rules, **kwargs):
    """Call Semgrep."""
    if platform.system() == 'Windows':
        return None
    from semgrep import semgrep_main, util
    from semgrep.constants import OutputFormat
    from semgrep.output import OutputHandler, OutputSettings
    try:
        cpu_count = multiprocessing.cpu_count()
    except NotImplementedError:
        cpu_count = 1  # CPU count is not implemented on Windows
    # Semgrep output formatting
    util.set_flags(
        verbose=False,
        debug=False,
        quiet=True,
        force_color=False)
    output_settings = OutputSettings(
        output_format=OutputFormat.JSON,
        output_destination=None,
        error_on_findings=False,
        verbose_errors=False,
        strict=False,
        timeout_threshold=3,
        json_stats=False,
        output_per_finding_max_lines_limit=None,
    )
    output_handler = OutputHandler(output_settings)
    (
        filtered_matches_by_rule,
        _all_targets,
        _filtered_rules,
        _profiler,
        _profiling_data,
        _shown_severities,
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
