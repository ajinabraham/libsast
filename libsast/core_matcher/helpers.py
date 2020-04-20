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
        raise RuleDownloadException
    return False


def read_yaml(file_obj, text=False):
    try:
        if text:
            return yaml.safe_load(file_obj)
        return yaml.safe_load(file_obj.read_text('utf-8', 'ignore'))
    except yaml.YAMLError:
        raise YamlRuleParseError
    except Exception:
        raise YamlRuleLoadException


def get_rules(rule_loc):
    """Get pattern matcher rules."""
    if not rule_loc:
        raise MissingRuleError
        return
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
                patterns.extend(read_yaml(yfile))
            return patterns
        else:
            raise InvalidRuleError
