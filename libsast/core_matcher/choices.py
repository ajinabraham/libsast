# -*- coding: utf_8 -*-
"""Alogrithms for Choice Selection."""
import re


def find_choices(data, rule):
    """Find Choices.

    or - returns list on first match
    and - returns list on first match
    all - returns set
    """
    all_matches = set()
    for idx, choice in enumerate(rule['choice']):
        typ = rule['choice_type']
        if typ == 'and':
            # Return on first and choice
            for idx, and_list in enumerate(rule['choice']):
                for and_regx in and_list[0]:
                    if not re.compile(and_regx).findall(data):
                        break
                else:
                    return [idx]
        elif re.compile(choice[0]).findall(data):
            if typ == 'or':
                # Return on first or choice
                return [idx]
            elif typ == 'all':
                # Extract all choice(s) from all files
                all_matches.add(choice[1])
    return all_matches
