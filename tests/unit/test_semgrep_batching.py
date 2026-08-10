# -*- coding: utf_8 -*-
"""Unit tests for Semgrep argv batching (MobSF/mobsfscan#98)."""
import errno

from libsast.core_sgrep.helpers import (
    _invoke_semgrep_batched,
    batch_paths,
    merge_semgrep_reports,
)


def test_batch_paths_respects_byte_budget():
    base = ['semgrep', 'scan', '--json', '--config', 'rules.yaml']
    paths = [f'/tmp/project/file_{i}.java' for i in range(50)]
    batches = batch_paths(base, paths, max_bytes=400)
    assert len(batches) > 1
    assert sum(len(batch) for batch in batches) == len(paths)
    for batch in batches:
        size = sum(len(p) + 1 for p in base + batch)
        # First path in a batch may exceed alone; later ones must fit budget
        # when batch has multiple entries.
        if len(batch) > 1:
            assert size <= 400


def test_batch_paths_empty():
    assert batch_paths(['semgrep'], [], max_bytes=100) == [[]]


def test_merge_semgrep_reports():
    merged = merge_semgrep_reports([
        {'results': [{'check_id': 'a'}], 'errors': ['e1']},
        {'results': [{'check_id': 'b'}], 'errors': []},
        None,
        {'results': [], 'errors': 'e2'},
    ])
    assert [r['check_id'] for r in merged['results']] == ['a', 'b']
    assert merged['errors'] == ['e1', 'e2']


def test_invoke_bisects_on_e2big(monkeypatch):
    """When argv is too long, bisect batches until calls succeed."""
    calls = []

    def fake_run(command):
        calls.append(list(command))
        paths = command[len([
            'semgrep', 'scan', '--metrics=off', '--disable-version-check',
            '--quiet', '--no-rewrite-rule-ids', '--json', '--config', 'r',
        ]):]
        # Fail if more than 2 paths (simulate ARG_MAX)
        if len(paths) > 2:
            raise OSError(errno.E2BIG, 'Argument list too long')
        return {
            'results': [{'path': p} for p in paths],
            'errors': [],
        }

    monkeypatch.setattr(
        'libsast.core_sgrep.helpers._run_semgrep_command', fake_run)

    base = [
        'semgrep', 'scan', '--metrics=off', '--disable-version-check',
        '--quiet', '--no-rewrite-rule-ids', '--json', '--config', 'r',
    ]
    paths = [f'f{i}.java' for i in range(5)]
    # Force a single oversized batch so bisect path is exercised
    report = _invoke_semgrep_batched(base, paths, max_bytes=10 ** 9)
    assert len(report['results']) == 5
    assert report['errors'] == []
    # At least one call must have split (more than one successful run)
    assert len(calls) >= 3
