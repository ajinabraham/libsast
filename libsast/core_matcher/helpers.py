# -*- coding: utf_8 -*-
"""Helper Functions."""
from pathlib import Path

from libsast.logger import init_logger

import yaml

import requests

logger = init_logger(__name__)


def download_rule(url):
    """Download Pattern File."""
    try:
        with requests.get(url, allow_redirects=True) as r:
            r.raise_for_status()
            return r.text
    except requests.exceptions.RequestException:
        logger.exception('Failed to download '
                         'patterns from url: %s', url)
    return False


def read_yaml(file_obj, text=False):
    try:
        if text:
            return yaml.safe_load(file_obj)
        return yaml.safe_load(file_obj.read_text('utf-8', 'ignore'))
    except yaml.YAMLError:
        logger.error('Failed to parse YAML')
    except Exception:
        logger.exception('Error parsing YAML')


def get_rules(rule_loc):
    """Get pattern matcher rules."""
    if not rule_loc:
        logger.error('No rule directory, file or url specified')
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
            logger.error('Not a valid file or directory: %s', rule)
