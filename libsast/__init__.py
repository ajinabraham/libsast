#!/usr/bin/env python
# -*- coding: utf_8 -*-

from .scanner import Scanner
from .core_matcher.pattern_matcher import PatternMatcher


__title__ = 'libsast'
__authors__ = 'Ajin Abraham'
__copyright__ = 'Copyright 2020 Ajin Abraham, OpenSecurity'
__version__ = '1.0.0'
__version_info__ = tuple(int(i) for i in __version__.split('.'))
__all__ = [
    'Scanner',
    'PatternMatcher',
    '__title__',
    '__authors__',
    '__copyright__',
    '__version__',
    '__version_info__',
]
