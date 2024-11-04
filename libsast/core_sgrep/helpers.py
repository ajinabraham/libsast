# -*- coding: utf_8 -*-
"""Semantic Grep Helpers."""
import json
import platform
import subprocess


def invoke_semgrep(paths, scan_rules):
    if platform.system() == 'Windows':
        return None
    ps = [pt.as_posix() for pt in paths]
    command = [
        'semgrep',
        '--metrics=off',
        '--no-rewrite-rule-ids',
        '--json',
        '-q',
        '--config',
        scan_rules,
        *ps,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        try:
            return json.loads(e.output)
        except json.JSONDecodeError:
            return {'errors': e.output}
