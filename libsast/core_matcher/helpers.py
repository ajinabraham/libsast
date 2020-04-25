# -*- coding: utf_8 -*-
"""Helper Functions."""
from pathlib import Path

from libsast.exceptions import (
    InvalidRuleError,
    MissingRuleError,
    RuleDownloadException,
    YamlRuleLoadException,
    YamlRuleParseError,
)

import yaml

import requests


def download_rule(url):
    """Download Pattern File."""
    try:
        with requests.get(url, allow_redirects=True) as r:
            r.raise_for_status()
            return r.text
    except requests.exceptions.RequestException:
        raise RuleDownloadException(f'Failed to download from: {url}')


def read_yaml(file_obj, text=False):
    try:
        if text:
            return yaml.safe_load(file_obj)
        return yaml.safe_load(file_obj.read_text('utf-8', 'ignore'))
    except yaml.YAMLError as exp:
        raise YamlRuleParseError(
            f'YAML Parse Error: {repr(exp)}')
    except Exception as gen:
        raise YamlRuleLoadException(
            f'Failed to load YAML file: {repr(gen)}')


def get_rules(rule_loc):
    """Get pattern matcher rules."""
    if not rule_loc:
        raise MissingRuleError('Rule location is not missing.')
    if rule_loc.startswith(('http://', 'https://')):
        pat = download_rule(rule_loc)
        if not pat:
            return
        return read_yaml(pat, True)
    else:
        rule = Path(rule_loc)
        if rule.is_file() and rule.exists():
            return read_yaml(rule)
        elif rule.is_dir() and rule.exists():
            patterns = []
            for yfile in rule.glob('**/*.yaml'):
                rule = read_yaml(yfile)
                if rule:
                    patterns.extend(rule)
            return patterns
        else:
            raise InvalidRuleError('This path is invalid')
