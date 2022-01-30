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
        if not rule.get('metadata'):
            new_rules.append(rule)
            continue
        meta_keys = rule['metadata'].keys()
        for mkey in meta_keys:
            if mkey not in std_map.keys():
                continue
            to_expand = rule['metadata'][mkey]
            expanded = std_map[mkey].get(to_expand)
            if expanded:
                rule['metadata'][mkey] = expanded
        new_rules.append(rule)
    return new_rules
