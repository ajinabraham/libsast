# -*- coding: utf_8 -*-
"""Semantic Grep Helpers."""
import json
import platform
import subprocess
from pathlib import Path

# Semgrep CE redacts some JSON fields unless logged into Semgrep App.
_REDACTED = 'requires login'


def invoke_semgrep(paths, scan_rules):
    """Call Semgrep and return the parsed JSON report."""
    if platform.system() == 'Windows':
        return None
    ps = [pt.as_posix() for pt in paths]
    command = [
        'semgrep',
        'scan',
        '--metrics=off',
        '--disable-version-check',
        '--quiet',
        '--no-rewrite-rule-ids',
        '--json',
        '--config',
        scan_rules,
        *ps,
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        raw = result.stdout or ''
        if not raw:
            err = (result.stderr or '').strip()
            return {'results': [], 'errors': [err] if err else []}
        return json.loads(raw)
    except FileNotFoundError:
        return {
            'results': [],
            'errors': ['semgrep not found. Install with: pip install semgrep'],
        }
    except json.JSONDecodeError as exc:
        return {'results': [], 'errors': [str(exc)]}


def get_match_string(path, start_line, end_line, fallback=''):
    """Return matched source text, recovering it when Semgrep redacts lines."""
    if fallback and fallback != _REDACTED:
        return fallback
    try:
        lines = Path(path).read_text(
            encoding='utf-8', errors='ignore').splitlines()
        snippet = lines[start_line - 1:end_line]
        return '\n'.join(snippet)
    except (OSError, ValueError, IndexError, TypeError):
        return '' if fallback == _REDACTED else fallback
