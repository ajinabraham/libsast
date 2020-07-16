# -*- coding: utf_8 -*-
"""Semantic Grep Helpers."""
import multiprocessing
from io import StringIO
import json


from semgrep.constants import OutputFormat
from semgrep.output import (
    OutputHandler,
    OutputSettings,
)
from semgrep import semgrep_main, util

try:
    CPU_COUNT = multiprocessing.cpu_count()
except NotImplementedError:
    CPU_COUNT = 1  # CPU count is not implemented on Windows


def invoke_semgrep(paths, scan_rules, **kwargs):
    """Call Semgrep."""
    util.set_flags(False, True, False)  # Verbose, Quiet, Force_color
    io_capture = StringIO()
    output_handler = OutputHandler(
        OutputSettings(
            output_format=OutputFormat.JSON,
            output_destination=None,
            error_on_findings=False,
            strict=False,
        ),
        stdout=io_capture,
    )
    semgrep_main.main(
        output_handler=output_handler,
        target=[pt.as_posix() for pt in paths],
        jobs=CPU_COUNT,
        pattern=None,
        lang=None,
        config=scan_rules,
        **kwargs,
    )
    output_handler.close()
    return json.loads(io_capture.getvalue())
