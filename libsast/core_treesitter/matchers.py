# -*- coding: utf_8 -*-
"""Tree-sitter AST Matching Strategies."""
from abc import ABC, abstractmethod
from functools import lru_cache

from tree_sitter import Parser, Query
try:
    from tree_sitter import QueryCursor
except ImportError:  # pragma: no cover
    QueryCursor = None

from libsast.core_treesitter.languages import get_language

_IDENTIFIER_TYPES = {
    'identifier',
    'simple_identifier',
    'property_identifier',
    'variable_name',
    'constant',
}
_DECLARATOR_TYPES = {
    'variable_declarator',
    'constant_declaration',
    'property_declaration',
    'assignment',
    'short_var_declaration',
}


@lru_cache(maxsize=256)
def get_compiled_query(lang_name, pattern):
    """Compile and cache a tree-sitter Query for a language."""
    lang = get_language(lang_name)
    text = str(pattern).strip()
    if '@match' not in text:
        text = f'{text} @match'
    return Query(lang, text)


def parse_tree(lang_name, source_bytes):
    """Parse source bytes into a tree-sitter Tree."""
    lang = get_language(lang_name)
    parser = Parser(lang)
    return parser.parse(source_bytes)


def _declarator_pair(node):
    """Return (name_node, val_node) if node is a constant/variable declarator."""
    if node.type not in _DECLARATOR_TYPES:
        return None, None
    name_node = node.child_by_field_name(
        'name') or node.child_by_field_name('left')
    val_node = node.child_by_field_name(
        'value') or node.child_by_field_name('right')
    if name_node is None or val_node is None:
        return None, None
    if name_node.type not in _IDENTIFIER_TYPES:
        return None, None
    return name_node, val_node


def extract_constants_map(root_node, source_bytes):
    """Extract a file-local map of identifier_bytes -> value_bytes."""
    consts = {}
    stack = [root_node]
    while stack:
        node = stack.pop()
        name_node, val_node = _declarator_pair(node)
        if name_node is not None:
            ident = source_bytes[name_node.start_byte:name_node.end_byte]
            if ident and ident not in consts:
                consts[ident] = source_bytes[
                    val_node.start_byte:val_node.end_byte]
        for child in node.children:
            if child.is_named:
                stack.append(child)
    return consts


def _is_declaration_or_callee(node):
    """Return True if identifier node is a declaration LHS or callee."""
    parent = node.parent
    if parent is None:
        return False
    for field in ('name', 'left', 'function'):
        if parent.child_by_field_name(field) == node:
            return True
    return False


def _collect_constant_replacements(root_node, source_bytes, consts):
    """Collect sorted (start, end, val_bytes) spans for identifier uses."""
    replacements = []
    stack = [root_node]
    while stack:
        node = stack.pop()
        if node.type in _IDENTIFIER_TYPES:
            ident = source_bytes[node.start_byte:node.end_byte]
            if ident in consts and not _is_declaration_or_callee(node):
                replacements.append((
                    node.start_byte, node.end_byte, consts[ident]))
            continue
        for child in node.children:
            if child.is_named:
                stack.append(child)
    replacements.sort(key=lambda item: item[0])
    return replacements


def inline_tree_constants(lang_name, tree, source_bytes):
    """Return a Tree with identifier uses replaced by their constant values."""
    consts = extract_constants_map(tree.root_node, source_bytes)
    if not consts:
        return tree
    replacements = _collect_constant_replacements(
        tree.root_node, source_bytes, consts)
    if not replacements:
        return tree
    out = bytearray()
    cursor = 0
    for start, end, val_bytes in replacements:
        if start >= cursor:
            out.extend(source_bytes[cursor:start])
            out.extend(val_bytes)
            cursor = end
    out.extend(source_bytes[cursor:])
    return parse_tree(lang_name, bytes(out))


def _query_matches(query, node):
    """Execute a Query against a Node across tree-sitter 0.22-0.26+."""
    if QueryCursor is not None:
        return QueryCursor(query).matches(node)
    return query.matches(node)


def _captured_nodes(query, root_node):
    """Return captured AST nodes for @match (or root capture of each match)."""
    matches = _query_matches(query, root_node)
    if not matches:
        return []
    nodes = []
    for _pattern_idx, cap_dict in matches:
        if 'match' in cap_dict:
            nodes.extend(cap_dict['match'])
            continue
        all_caps = [n for nlist in cap_dict.values() for n in nlist]
        if all_caps:
            outer = min(
                all_caps,
                key=lambda n: (n.start_byte, -(n.end_byte - n.start_byte)),
            )
            nodes.append(outer)
    return nodes


def _matches_subquery(lang_name, query_str, node):
    """Return True if query_str matches anywhere inside node."""
    if not query_str:
        return False
    q = get_compiled_query(lang_name, query_str)
    return bool(_captured_nodes(q, node))


def _has_matching_ancestor(lang_name, query_str, node, root_node):
    """Return True if node is inside any ancestor matched by query_str."""
    if not query_str:
        return False
    q = get_compiled_query(lang_name, query_str)
    ancestors = _captured_nodes(q, root_node)
    if not ancestors:
        return False
    n_start, n_end = node.start_byte, node.end_byte
    return any(
        a.start_byte <= n_start and n_end <= a.end_byte
        for a in ancestors
    )


def _node_passes_filters(node, root_node, lang_name, rule):
    """Check optional exclude_ancestor, within_ancestor, and not_within_node."""
    exclude_anc = rule.get('exclude_ancestor')
    if exclude_anc and _has_matching_ancestor(
            lang_name, exclude_anc, node, root_node):
        return False
    within_anc = rule.get('within_ancestor')
    if within_anc and not _has_matching_ancestor(
            lang_name, within_anc, node, root_node):
        return False
    not_within = rule.get('not_within_node')
    if not_within and _matches_subquery(lang_name, not_within, node):
        return False
    return True


def _format_node_match(node, source_bytes, max_len=300):
    """Convert a matched AST Node into a libsast (match_str, pos, lines) tuple."""
    start_row = node.start_point[0]
    end_row = node.end_point[0]
    src_lines = source_bytes.splitlines()
    if 0 <= start_row < len(src_lines) and end_row < len(src_lines):
        if start_row == end_row and len(src_lines[start_row]) <= max_len:
            raw = src_lines[start_row][
                node.start_point[1]:node.end_point[1]
            ].decode('utf-8', 'ignore').strip()
            if not raw:
                raw = src_lines[start_row].decode('utf-8', 'ignore').strip()
        else:
            chunk = b'\n'.join(src_lines[start_row:end_row + 1])
            raw = chunk.decode('utf-8', 'ignore').strip()
    else:
        raw = source_bytes[
            node.start_byte:node.end_byte
        ].decode('utf-8', 'ignore').strip()
    if max_len and len(raw) > max_len:
        raw = raw[:max_len]
    pos = (1 if node.start_byte == 0 else node.start_byte, node.end_byte)
    lines = (start_row + 1, end_row + 1)
    return (raw, pos, lines)


def find_query_matches(tree, source_bytes, lang_name, query_str, rule,
                       max_len=300):
    """Run a single S-expression query and return a set of formatted matches."""
    root = tree.root_node
    query = get_compiled_query(lang_name, query_str)
    matches = set()
    for node in _captured_nodes(query, root):
        if not _node_passes_filters(node, root, lang_name, rule):
            continue
        match_tuple = _format_node_match(node, source_bytes, max_len)
        if match_tuple[0]:
            matches.add(match_tuple)
    return matches


def rule_supports_language(rule, lang_name):
    """Return True if rule applies to lang_name."""
    langs = rule.get('languages')
    if not langs:
        return True
    if isinstance(langs, str):
        return langs.lower() == lang_name
    return lang_name in {str(x).lower() for x in langs}


class TSMatchStrategy(ABC):
    @abstractmethod
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len):
        """Search for AST pattern matches in tree."""


class TreeSitter(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len):
        patterns = rule['pattern']
        if isinstance(patterns, list):
            matches = set()
            for pat in patterns:
                matches.update(find_query_matches(
                    tree, source_bytes, lang_name, pat, rule, max_len))
            return matches
        return find_query_matches(
            tree, source_bytes, lang_name, patterns, rule, max_len)


class TreeSitterAnd(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len):
        patterns = rule['pattern'] if isinstance(
            rule['pattern'], list) else [rule['pattern']]
        all_matches = set()
        for pat in patterns:
            matches = find_query_matches(
                tree, source_bytes, lang_name, pat, rule, max_len)
            if not matches:
                return False
            all_matches.update(matches)
        return all_matches


class TreeSitterOr(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len):
        patterns = rule['pattern'] if isinstance(
            rule['pattern'], list) else [rule['pattern']]
        matches = set()
        for pat in patterns:
            matches.update(find_query_matches(
                tree, source_bytes, lang_name, pat, rule, max_len))
        return matches


class TreeSitterAndNot(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len):
        present_pat, absent_pat = rule['pattern']
        absent_matches = find_query_matches(
            tree, source_bytes, lang_name, absent_pat, {}, max_len)
        if absent_matches:
            return False
        present_matches = find_query_matches(
            tree, source_bytes, lang_name, present_pat, rule, max_len)
        return present_matches if present_matches else False


class TreeSitterAndOr(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len):
        and_pat, or_pats = rule['pattern']
        and_matches = find_query_matches(
            tree, source_bytes, lang_name, and_pat, rule, max_len)
        if not and_matches:
            return False
        for pat in or_pats:
            or_matches = find_query_matches(
                tree, source_bytes, lang_name, pat, rule, max_len)
            if or_matches:
                return and_matches.union(or_matches)
        return False


TS_MATCHERS = {
    'TreeSitter': TreeSitter,
    'TreeSitterAnd': TreeSitterAnd,
    'TreeSitterOr': TreeSitterOr,
    'TreeSitterAndNot': TreeSitterAndNot,
    'TreeSitterAndOr': TreeSitterAndOr,
}
