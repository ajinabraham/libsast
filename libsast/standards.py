# -*- coding: utf_8 -*-
"""Standards Matcher."""
from pathlib import Path

from libsast.common import (
    read_yaml,
)


def read_standards(rule_loc):
    """Get mappings."""
    if rule_loc.is_dir() and rule_loc.exists():
        patterns = {}
        for yfile in rule_loc.glob('**/*.yaml'):
            rule = read_yaml(yfile)
            if rule:
                patterns.update(rule)
        return patterns
    return None


def get_standards():
    """Get inbuilt mappings."""
    stds_loc = Path(__file__).parents[0] / 'standards'
    return read_standards(stds_loc)


def get_mapping(rules):
    """Process rule mappings."""
    std_map = get_standards()
    new_rules = []
    for rule in rules:
        for key in rule.keys():
            if key in std_map.keys():
                rule[key] = std_map[key].get(rule[key], rule[key])
        new_rules.append(rule)
    return new_rules
