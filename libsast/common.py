# -*- coding: utf_8 -*-
"""Common Helpers."""
import os
import sys
from threading import Thread

from libsast.exceptions import (
    YamlRuleLoadError,
    YamlRuleParseError,
)

import yaml


class ProgressBar:
    def __init__(self, prefix, expected_time, size=60, output=sys.stderr):
        self.prefix = prefix
        self.expected_time = expected_time
        self.size = size
        self.output = output

    def progress_print(self, index):
        """Print progress bar."""
        prog_length = int(self.size * index / self.expected_time)
        prog = '█' * prog_length
        self.output.write(f'- {self.prefix} {prog} {index}\r')
        self.output.flush()

    def progress_loop(self, iterator):
        """Show progress for loop."""
        self.progress_print(0)
        for index, item in enumerate(iterator):
            yield item
            self.progress_print(index + 1)
        self.output.write('\n')
        self.output.flush()

    def progress_function(self, function, args=None, kwargs=None):
        """Show progress for function."""
        ret = [None]
        index = 0
        # Hack determined by size of rule files
        self.expected_time = self.expected_time * 350

        def myrunner(function, ret, *args, **kwargs):
            ret[0] = function(*args, **kwargs)
        self.progress_print(0)
        thread = Thread(
            target=myrunner,
            args=(function, ret) + tuple(args),
            kwargs=kwargs)
        thread.start()
        while thread.is_alive():
            thread.join(timeout=0.2)
            index += 1
            self.progress_print(index)
        self.output.write('\n')
        self.output.flush()
        return ret[0]


def read_yaml(file_obj, text=False):
    try:
        if text:
            return yaml.safe_load(file_obj)
        return yaml.safe_load(file_obj.read_text('utf-8', 'ignore'))
    except yaml.YAMLError as exp:
        raise YamlRuleParseError(
            f'YAML Parse Error: {repr(exp)}')
    except Exception as gen:
        raise YamlRuleLoadError(
            f'Failed to load YAML file: {repr(gen)}')


def get_worker_count():
    """Get worker count for pool."""
    libsast_workers = os.getenv('LIBSAST_WORKERS')
    if libsast_workers:
        try:
            return int(libsast_workers)
        except ValueError:
            return 1
    try:
        worker_count = os.cpu_count()
    except Exception:
        worker_count = 1

    # Adjust worker count for Windows
    if sys.platform == 'win32':
        worker_count = min(worker_count, 61)
    return worker_count
