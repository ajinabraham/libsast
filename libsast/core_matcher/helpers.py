# -*- coding: utf_8 -*-
"""Helper Functions."""
import re
from pathlib import Path

from libsast.exceptions import (
    InvalidRuleError,
    MissingRuleError,
    RuleDownloadError,
)
from libsast.common import read_yaml
from libsast.standards import get_mapping

import requests

# Default Single Line
DEF_SINGLE = re.compile(r'//.+', re.MULTILINE)
DEF_MULTI = re.compile(r'/\*([\S|\s]+?)\*/', re.MULTILINE)
XML_CMT = re.compile(r'<!--([\S|\s]+?)-->', re.MULTILINE)


def download_rule(url):
    """Download Pattern File."""
    try:
        with requests.get(
                url,
                allow_redirects=True,
                timeout=10) as r:
            r.raise_for_status()
            return r.text
    except requests.exceptions.RequestException:
        raise RuleDownloadError(f'Failed to download from: {url}')


def get_rules(rule_loc):  # noqa: R701
    """Get pattern matcher rules."""
    if not rule_loc:
        raise MissingRuleError('Rule location is missing.')
    if rule_loc.startswith(('http://', 'https://')):
        pat = download_rule(rule_loc)
        if not pat:
            return
        rules = read_yaml(pat, True)
        if not rules:
            return
        return get_mapping(rules)
    rule = Path(rule_loc)
    if rule.is_file() and rule.exists():
        rules = read_yaml(rule)
        if not rules:
            return
        return get_mapping(rules)
    elif rule.is_dir() and rule.exists():
        patterns = []
        for yfile in rule.glob('**/*.yaml'):
            rules = read_yaml(yfile)
            if rules:
                rules = get_mapping(rules)
                patterns.extend(rules)
        return patterns
    else:
        raise InvalidRuleError('This path is invalid')


def comment_replacer(matches, data):
    """Replace Comments from data."""
    to_replace = set()
    repl_regex = re.compile(r'\S', re.MULTILINE)
    for match in matches:
        if match.group():
            stripm = match.group().strip()
            if stripm == '//':
                # ignore comment starters
                continue
            if ':' + stripm in data:
                # possible URLs http://, do not strip
                continue
            if 'ignore:' in data:
                # preserve ignore tags
                continue
            to_replace.add(match.group())
    for itm in to_replace:
        dummy = repl_regex.sub(' ', itm)
        data = data.replace(itm, dummy)
    return data


def strip_comments1(data):
    """Remove Comments.

    Replace multiline comments first and
    then replace single line comments.
    """
    single_line = DEF_SINGLE
    multi_line = DEF_MULTI
    mmatches = multi_line.finditer(data)
    data = comment_replacer(mmatches, data)
    smatches = single_line.finditer(data)
    data = comment_replacer(smatches, data)
    return data


def strip_comments2(data):
    """Remove Comments 2.

    Replace comments for HTML/XML
    """
    multi_line = XML_CMT
    mmatches = multi_line.finditer(data)
    data = comment_replacer(mmatches, data)
    return data


def get_match_lines(content, pos):
    """Get Match lines from position."""
    start_line = 0
    filepos = 0
    skip = False
    for idx, line in enumerate(content.split('\n'), 1):
        filepos += len(line) + 1
        if filepos >= pos[0] and filepos >= pos[1] and not skip:
            # Match is on the same line
            return (idx, idx)
        elif filepos >= pos[0] and not skip:
            # Multiline match, find start line
            skip = True
            start_line = idx
        if filepos >= pos[1] and skip:
            # Multiline march, find end line
            return (start_line, idx)


def is_file_valid(sfile, allowed_extensions=None, max_size_mb=5):
    """Check if the file is valid based on its extension and size.

    Args:
        sfile (Path): The file to check.
        allowed_extensions (set): A set of allowed file extensions.
        max_size_mb (int): The maximum file size in MB.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    # Get the file extension in lowercase
    ext = sfile.suffix.lower()

    # Check if the file extension is allowed
    if allowed_extensions and ext not in allowed_extensions:
        return False

    # Check if the file size exceeds the maximum limit (in bytes)
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if sfile.stat().st_size > max_size_bytes:
        return False

    return True


def strip_comments(data, ext):
    """Format content by stripping comments based on file type."""
    if ext in ('.html', '.xml'):
        return strip_comments2(data)
    return strip_comments1(data)
