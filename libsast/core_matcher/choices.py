# -*- coding: utf_8 -*-
"""Alogrithms for Choice Selection."""
import re


def find_choices(data, rule):
    """Fince Choices.

    Find or choices & and choices.
    or - returns tuple
    and - returns set
    """
    options = set()
    for idx, choice in enumerate(rule['choice']):
        if re.compile(choice[0]).findall(data):
            if rule['choice_type'] == 'or':
                # Priority for first choice
                return idx
            elif rule['choice_type'] == 'and':
                # Extrace all choice(s) from all files
                options.add(choice[1])
    return options
