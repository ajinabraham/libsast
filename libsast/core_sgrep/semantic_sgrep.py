# -*- coding: utf_8 -*-
"""Semantic Grep Core."""
import collections
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
)

from evaluation import (
    build_boolean_expression,
    evaluate_expression,
)

from sgrep_main import (
    build_normal_output,
    config_resolver,
    flatten_configs,
    flatten_rule_patterns,
    invoke_sgrep,
    parse_sgrep_output,
    rewrite_message_with_metavars,
    safe_relative_to,
    sgrep_finding_to_range,
    validate_configs,
)

from libsast.logger import init_logger

logger = init_logger(__name__)


class SemanticGrep:
    def __init__(self, options: dict) -> None:
        self.scan_rules = self.get_rules(options.get('sgrep_rules'))
        if options.get('match_extensions'):
            self.exts = options.get('match_extensions')
        else:
            self.exts = []
        if options.get('ignore_extensions'):
            self.ignore_extensions = options.get('ignore_extensions')
        else:
            self.ignore_extensions = []
        if options.get('ignore_filenames'):
            self.ignore_filenames = options.get('ignore_filenames')
        else:
            self.ignore_filenames = []
        if options.get('ignore_paths'):
            self.ignore_paths = options.get('ignore_paths')
        else:
            self.ignore_paths = []
        self.findings = {}

    def get_rules(self, rules):
        # TODO Handle invalid or may be support strict and validate
        """Process Sgrep Config."""
        configs = config_resolver.resolve_config(rules)
        valid_configs, _ = validate_configs(configs)
        all_rules = flatten_configs(valid_configs)
        all_patterns = list(flatten_rule_patterns(all_rules))
        return (all_rules, all_patterns)

    def scan(self, paths: list) -> dict:
        """Do sgrep scan."""
        all_rules = self.scan_rules[0]
        all_patterns = self.scan_rules[1]
        # TODO change to master
        sgrep_out = invoke_sgrep(all_patterns, paths)
        return self.process_output(all_rules, sgrep_out)

    def process_output(self, all_rules, output_json):
        """Actual Output Processing."""
        # TODO Change to master branch processing
        # Actual SGREP to Readable Processing
        # group output; we want to see all of
        # the same rule ids on the same file path
        by_rule_index: Dict[int, Dict[str, List[Dict[
            str, Any]]]] = collections.defaultdict(
                lambda: collections.defaultdict(list))

        sgrep_errors = output_json['errors']

        for finding in sgrep_errors:
            path = finding['path']
            check_id = finding['check_id']
            logger.error('sgrep: %s: %s', path, check_id)

        for finding in output_json['matches']:
            # decode the rule index from the output check_id
            rule_index = int(finding['check_id'].split('.')[0])
            by_rule_index[rule_index][finding['path']].append(finding)

        current_path = Path.cwd()
        outputs_after_booleans = []

        for rule_index, paths in by_rule_index.items():
            expression = build_boolean_expression(all_rules[rule_index])
            for _, results in paths.items():
                check_ids_to_ranges = parse_sgrep_output(results)
                valid_ranges_to_output = evaluate_expression(
                    expression,
                    check_ids_to_ranges,
                )
                # only output matches which are inside these offsets!
                for result in results:
                    if sgrep_finding_to_range(
                            result).range in valid_ranges_to_output:
                        path_object = Path(result['path'])

                        # restore the original rule ID
                        result['check_id'] = all_rules[rule_index]['id']
                        # rewrite the path to be relative to
                        # the current working directory
                        result['path'] = str(
                            safe_relative_to(path_object, current_path))

                        # restore the original message
                        result['extra'][
                            'message'] = rewrite_message_with_metavars(
                                all_rules[rule_index], result)
                        outputs_after_booleans.append(result)
        output_data = {
            'results': outputs_after_booleans,
        }
        logger.info('\n'.join(build_normal_output(
            output_data, color_output=True)))
        return {}
