# -*- coding: utf_8 -*-
"""Common Helpers."""
import sys
from threading import Thread


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

    def progrees_loop(self, iterator):
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
        self.expected_time = (
            self.expected_time if self.expected_time > 34 else 53)

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
