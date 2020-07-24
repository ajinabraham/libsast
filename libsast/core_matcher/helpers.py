# -*- coding: utf_8 -*-
"""Helper Functions."""
from pathlib import Path

from libsast.exceptions import (
    InvalidRuleError,
    MissingRuleError,
    RuleDownloadException,
)
from libsast.common import read_yaml
from libsast.standards import get_mapping

import requests


def download_rule(url):
    """Download Pattern File."""
    try:
        with requests.get(url, allow_redirects=True) as r:
            r.raise_for_status()
            return r.text
    except requests.exceptions.RequestException:
        raise RuleDownloadException(f'Failed to download from: {url}')


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
