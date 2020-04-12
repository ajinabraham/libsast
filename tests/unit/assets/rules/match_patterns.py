# -*- coding: utf_8 -*-
"""Standards Supported."""

from libsast.core_matcher.matchers import (
    InputCase,
    Level,
    Regex,
    RegexAnd,
    RegexAndNot,
    RegexAndOr,
    RegexOr,
)


RULES = [
    {
        'id': 'test_regex',
        'description': 'This is a rule to test regex',
        'type': Regex,
        'pattern': r'\.close\(\)',
        'severity': Level.info,
        'input_case': InputCase.exact,
    },
    {
        'id': 'test_regex_and',
        'description': 'This is a rule to test regex_and',
        'type': RegexAnd,
        'pattern': [r'\.loadUrl\(.*getExternalStorageDirectory\(',
                    r'webkit\.WebView'],
        'severity': Level.error,
        'input_case': InputCase.exact,
    },
    {
        'id': 'test_regex_or',
        'description': 'This is a rule to test regex_or',
        'type': RegexOr,
        'pattern': [r'MODE_WORLD_READABLE|Context\.MODE_WORLD_READABLE',
                    r'openFileOutput\(\s*".+"\s*,\s*1\s*\)'],
        'severity': Level.error,
        'input_case': InputCase.exact,
    },
    {
        'id': 'test_regex_and_not',
        'description': 'This is a rule to test regex_and_not',
        'type': RegexAndNot,
        'pattern': [r'WKWebView', r'\.javaScriptEnabled=false'],
        'severity': Level.warning,
        'input_case': InputCase.exact,
    },
    {
        'id': 'test_regex_and_or',
        'description': 'This is a rule to test regex_and_or',
        'type': RegexAndOr,
        'pattern': [r'telephony.SmsManager',
                    [r'sendMultipartTextMessage',
                     r'sendTextMessage', r'vnd.android-dir/mms-sms']],
        'severity': Level.warning,
        'input_case': InputCase.exact,
    },
]
