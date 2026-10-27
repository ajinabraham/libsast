# -*- coding: utf_8 -*-
"""Scanned file names must never be read as Semgrep options."""
import platform
import shutil
from pathlib import Path

import pytest

import libsast
from libsast.core_sgrep.helpers import invoke_semgrep

ASSETS = Path(__file__).parents[1] / 'assets'
OPTION_NAME = '--output=pwned.py'


@pytest.mark.skipif(platform.system() == 'Windows', reason='No Semgrep')
def test_paths_follow_end_of_options(monkeypatch):
    commands = []

    def fake_run(command):
        commands.append(list(command))
        return {'results': [], 'errors': []}

    monkeypatch.setattr(
        'libsast.core_sgrep.helpers._run_semgrep_command', fake_run)
    invoke_semgrep([Path(OPTION_NAME), Path('app.py')], 'rules')
    command = commands[0]
    assert command[-3:] == ['--', OPTION_NAME, 'app.py']
    assert command.index('--') > command.index('rules')


@pytest.mark.skipif(
    platform.system() == 'Windows' or not shutil.which('semgrep'),
    reason='Semgrep not available')
def test_option_named_file_is_scanned_as_path(tmp_path, monkeypatch):
    shutil.copy(ASSETS / 'files' / 'example_file.py', tmp_path / 'app.py')
    (tmp_path / OPTION_NAME).write_text('x = 1\n')
    monkeypatch.chdir(tmp_path)
    options = {
        'sgrep_rules': (ASSETS / 'rules' / 'semantic_grep').as_posix(),
        'sgrep_extensions': {'.py'},
    }
    result = libsast.Scanner(options, ['.']).scan()
    assert not (tmp_path / 'pwned.py').exists()
    assert result['semantic_grep']['matches']
