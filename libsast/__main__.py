# !/usr/bin/env python
# -*- coding: utf_8 -*-
"""libsast cli."""
import argparse
import json
import sys

from libsast import __version__
from libsast.scanner import Scanner


def output(out, scan_results):
    """Output."""
    if out:
        with open(out, 'w') as outfile:
            json.dump(scan_results,
                      outfile,
                      sort_keys=True,
                      indent=2,
                      separators=(',', ': '))
    else:
        if scan_results:
            print(json.dumps(scan_results,
                             sort_keys=True,
                             indent=2,
                             separators=(',', ': ')))
    if scan_results:
        sgrep_out = scan_results.get('semantic_grep', {}).get('matches')
        matcher_out = scan_results.get('pattern_matcher')
        if sgrep_out or matcher_out:
            sys.exit(1)
    sys.exit(0)


def main():
    """Main CLI."""
    parser = argparse.ArgumentParser()
    parser.add_argument('path',
                        nargs='*',
                        help=('Path can be file(s) or '
                              'directories'))
    parser.add_argument('-o', '--output',
                        help='Output filename to save JSON report.',
                        required=False)
    parser.add_argument('-p', '--pattern-file',
                        help='YAML pattern file, directory or url',
                        required=False)
    parser.add_argument('-s', '--sgrep-pattern-file',
                        help='sgrep rules directory',
                        required=False)
    parser.add_argument('--sgrep-file-extensions',
                        nargs='+',
                        help=('File extensions that should be scanned'
                              ' with sgrep'),
                        required=False)
    parser.add_argument('--file-extensions',
                        nargs='+',
                        help=('File extensions that should be scanned'
                              ' with pattern matcher'),
                        required=False)
    parser.add_argument('--ignore-filenames',
                        nargs='+',
                        help='File name(s) to ignore',
                        required=False)
    parser.add_argument('--ignore-extensions',
                        nargs='+',
                        help='File extension(s) to ignore in lower case',
                        required=False)
    parser.add_argument('--ignore-paths',
                        nargs='+',
                        help='Path(s) to ignore',
                        required=False)
    parser.add_argument('--show-progress',
                        help='Show scan progress',
                        required=False,
                        action='store_true')
    parser.add_argument('-v', '--version',
                        help='Show libsast version',
                        required=False,
                        action='store_true')
    args = parser.parse_args()
    if args.path and (args.pattern_file or args.sgrep_pattern_file):
        options = {
            'sgrep_rules': args.sgrep_pattern_file,
            'sgrep_extensions': args.sgrep_file_extensions,
            'match_rules': args.pattern_file,
            'match_extensions': args.file_extensions,
            'ignore_filenames': args.ignore_filenames,
            'ignore_extensions': args.ignore_extensions,
            'ignore_paths': args.ignore_paths,
            'show_progress': args.show_progress,
        }
        result = Scanner(options, args.path).scan()
        output(args.output, result)
    elif args.version:
        print(f'libsast v{__version__}')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
