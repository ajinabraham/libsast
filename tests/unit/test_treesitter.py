# -*- coding: utf_8 -*-
"""Unit tests for Tree-sitter AST matcher."""
from pathlib import Path

import pytest

from libsast import Scanner, TreeSitterMatcher, exceptions

ASSETS_DIR = Path(__file__).parents[1] / 'assets'
TS_FILES_DIR = ASSETS_DIR / 'files' / 'treesitter'
TS_RULES_FILE = ASSETS_DIR / 'rules' / 'treesitter_matcher' / 'ts_rules.yaml'
INVALID_TS_LANG_FILE = ASSETS_DIR / 'invalid' / 'invalid_ts_lang.yaml'


def test_treesitter_tsx_and_dev_guard_and_not_within():
    tsx_file = TS_FILES_DIR / 'App.tsx'
    res = Scanner(
        {'match_rules': TS_RULES_FILE.as_posix(), 'multiprocessing': 'thread'},
        [tsx_file.as_posix()],
    ).scan()['pattern_matcher']

    eval_matches = res['ts_eval_call']['files']
    assert len(eval_matches) == 1
    assert eval_matches[0]['match_lines'] == (5, 5)
    assert eval_matches[0]['match_string'] == 'eval("prod_danger")'

    mmkv_matches = res['ts_mmkv_missing_encryption']['files']
    assert len(mmkv_matches) == 1
    assert mmkv_matches[0]['match_lines'] == (7, 7)

    wv_matches = res['ts_webview_universal_access']['files']
    assert len(wv_matches) == 1
    assert wv_matches[0]['match_lines'] == (9, 12)


def test_treesitter_minified_bundle_and_html_script():
    bundle = TS_FILES_DIR / 'index.android.bundle'
    html = TS_FILES_DIR / 'index.html'
    res = Scanner(
        {'ts_rules': TS_RULES_FILE.as_posix(), 'multiprocessing': 'thread'},
        [bundle.as_posix(), html.as_posix()],
    ).scan()['treesitter_matcher']

    assert res['ts_webview_universal_access']['files'][0]['match_string'] == (
        'allowUniversalAccessFromFileURLs:!0'
    )
    assert 'ts_and_rule' in res
    assert 'ts_and_not_rule' in res
    assert res['ts_eval_call']['files'][0]['match_lines'] == (3, 3)


def test_treesitter_resolves_intra_file_constants():
    ts_file = TS_FILES_DIR / 'storage.ts'
    res = Scanner(
        {'ts_rules': TS_RULES_FILE.as_posix(), 'multiprocessing': 'thread'},
        [ts_file.as_posix()],
    ).scan()['treesitter_matcher']

    assert 'ts_async_storage_sensitive_key' in res
    matches = res['ts_async_storage_sensitive_key']['files']
    assert len(matches) == 1
    assert matches[0]['match_lines'] == (4, 4)


def test_treesitter_missing_grammar_raises():
    custom_file = TS_FILES_DIR / 'a.custom'
    matcher = TreeSitterMatcher({
        'ts_rules': INVALID_TS_LANG_FILE.as_posix(),
        'ts_extension_map': {'.custom': 'nonexistent_lang_xyz'},
        'multiprocessing': 'thread',
    })
    with pytest.raises(exceptions.MatcherNotFoundError):
        matcher.scan([custom_file])
