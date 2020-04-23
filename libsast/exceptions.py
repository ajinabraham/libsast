# -*- coding: utf_8 -*-
"""The libsast Exceptions."""


class LibsastException(Exception):
    """Base class for all exceptions thrown by libsast."""

    def __init__(self, message=None):
        super().__init__(message)


class InvalidPathError(LibsastException):
    """Invalid Path Supplied to libsast."""

    pass


class YamlRuleParseError(LibsastException):
    """Failed to parse YAML rule."""

    pass


class YamlRuleLoadException(LibsastException):
    """Failed to load YAML rule file."""

    pass


class MissingRuleError(LibsastException):
    """Rule not provided."""

    pass


class InvalidRuleError(LibsastException):
    """No rule directory, file or url specified."""

    pass


class TypeKeyMissingError(LibsastException):
    """Pattern Matcher rule does not have the key 'type'."""

    pass


class InvalidRuleFormatException(LibsastException):
    """Pattern Matcher rule file is invalid."""

    pass


class PatternKeyMissingError(LibsastException):
    """Pattern Matcher rule does not have the key 'pattern'."""

    pass


class RuleDownloadException(LibsastException):
    """Failed to download rule."""

    pass


class RuleProcessingException(LibsastException):
    """Failed to download rule."""

    pass


class MatcherNotFoundException(LibsastException):
    """Pattern Matcher not found."""

    pass
