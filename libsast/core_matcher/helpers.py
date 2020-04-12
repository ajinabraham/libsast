# -*- coding: utf_8 -*-
"""Helper Functions."""
import sys
from pathlib import Path

from libsast.logger import init_logger

logger = init_logger(__name__)


def get_rules(rules):
    """Get pattern matcher rules."""
    if not rules:
        logger.error('No rule directory specified')
        return
    rule_loc = rules
    rule = Path(rules)
    if rule.is_dir() and rule.exists():
        sys.path.append(rules)
    elif rule.is_file() and rule.exists():
        rule_loc = rule.parents[0].as_posix()
        sys.path.append(rule_loc)
    try:
        import match_patterns
        return match_patterns.RULES
    except ImportError:
        logger.error('Rule file match_patterns.py is not present in %s',
                     rule_loc)
    except SyntaxError:
        logger.error('Syntax error in match_patterns.py in %s', rule_loc)
    except Exception:
        logger.exception('Error loading match_patterns.py in %s', rule_loc)
    return
