"""Unit Tests - symlinks in the scanned tree are not followed."""
import os

import pytest

import libsast

from .setup_test import scanner


def test_symlinked_file_not_scanned(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'secret.test').write_text('secret')
    root = tmp_path / 'root'
    root.mkdir()
    real = root / 'real.test'
    real.write_text('real')
    try:
        os.symlink(outside / 'secret.test', root / 'link.test')
        os.symlink(outside, root / 'linked_dir')
    except (OSError, NotImplementedError):
        pytest.skip('Symlinks not supported')

    scan = libsast.Scanner({}, [root.as_posix()])
    assert scan.get_scan_files() == {real}
    assert not scan.validate_file(root / 'link.test')


def test_matcher_results_unaffected():
    options = {'match_extensions': ['.test']}
    assert scanner(options).scan()['pattern_matcher']['test_regex']
