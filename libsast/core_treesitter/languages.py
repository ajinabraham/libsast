# -*- coding: utf_8 -*-
"""Dynamic language grammar loader and extension mapping for tree-sitter."""
from functools import lru_cache
import importlib
import re

from tree_sitter import Language

from libsast import exceptions

DEFAULT_EXTENSION_MAP = {
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.bundle': 'javascript',
    '.jsbundle': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.vue': ('html_script', 'typescript'),
    '.svelte': ('html_script', 'typescript'),
    '.html': ('html_script', 'javascript'),
    '.htm': ('html_script', 'javascript'),
    '.java': 'java',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.swift': 'swift',
    '.m': 'objc',
    '.mm': 'objc',
    '.dart': 'dart',
    '.cs': 'c_sharp',
    '.py': 'python',
    '.rb': 'ruby',
    '.go': 'go',
    '.rs': 'rust',
    '.php': 'php',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.xml': 'xml',
    '.sh': 'bash',
}

_MODULE_OVERRIDE = {
    'tsx': ('tree_sitter_typescript', 'language_tsx'),
    'typescript': ('tree_sitter_typescript', 'language_typescript'),
    'c_sharp': ('tree_sitter_c_sharp', 'language'),
}
_SCRIPT_TAG_RE = re.compile(
    rb'<script\b[^>]*>(.*?)</script\s*>',
    re.IGNORECASE | re.DOTALL,
)


def _wrap_language(obj):
    """Wrap a PyCapsule or Language into a tree_sitter.Language instance."""
    if isinstance(obj, Language):
        return obj
    return Language(obj)


def _load_from_dedicated_package(lang_name):
    """Attempt to load a Language from a dedicated tree_sitter_<lang> module."""
    if lang_name in _MODULE_OVERRIDE:
        mod_name, fn_name = _MODULE_OVERRIDE[lang_name]
    else:
        mod_name = f'tree_sitter_{lang_name.replace("-", "_")}'
        fn_name = 'language'
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        return None
    for candidate in (fn_name, f'language_{lang_name}', 'language'):
        fn = getattr(mod, candidate, None)
        if callable(fn):
            return _wrap_language(fn())
    return None


def _load_from_language_pack(lang_name):
    """Attempt to load a Language from tree_sitter_language_pack."""
    try:
        pack = importlib.import_module('tree_sitter_language_pack')
        get_lang = getattr(pack, 'get_language', None)
        if callable(get_lang):
            return _wrap_language(get_lang(lang_name))
    except Exception:
        return None
    return None


@lru_cache(maxsize=64)
def get_language(lang_name):
    """Load and cache a tree-sitter Language by name."""
    norm = str(lang_name).strip().lower()
    lang = _load_from_dedicated_package(norm) or _load_from_language_pack(norm)
    if lang is not None:
        return lang
    raise exceptions.MatcherNotFoundError(
        f"Tree-sitter grammar for '{norm}' is not installed. "
        f"Install 'tree-sitter-{norm.replace('_', '-')}' or "
        f"'libsast[treesitter]'.")


def resolve_file_language(file_path, custom_ext_map=None):
    """Resolve (lang_name, is_embedded_script) for a file path."""
    ext = file_path.suffix.lower()
    ext_map = DEFAULT_EXTENSION_MAP
    if custom_ext_map:
        ext_map = {**DEFAULT_EXTENSION_MAP, **custom_ext_map}
    entry = ext_map.get(ext)
    if not entry:
        return None, False
    if isinstance(entry, (tuple, list)) and len(entry) == 2:
        return str(entry[1]).lower(), entry[0] == 'html_script'
    return str(entry).lower(), False


def extract_script_bytes(raw_bytes):
    """Blank out non-<script> regions while preserving exact line/byte offsets."""
    if b'<script' not in raw_bytes.lower():
        return b''
    out = bytearray(
        10 if b == 10 else (13 if b == 13 else 32)
        for b in raw_bytes
    )
    found = False
    for match in _SCRIPT_TAG_RE.finditer(raw_bytes):
        start, end = match.span(1)
        out[start:end] = raw_bytes[start:end]
        found = True
    return bytes(out) if found else b''
