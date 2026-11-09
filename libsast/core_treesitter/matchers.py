# -*- coding: utf_8 -*-
"""Tree-sitter AST Matching Strategies."""
from abc import ABC, abstractmethod
from bisect import bisect_right
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
    'variable_name',
    'constant',
}
_DECLARATOR_TYPES = {
    'variable_declarator',
    'constant_declaration',
    'property_declaration',
    'short_var_declaration',
}
_MUTATION_TYPES = {
    'assignment_expression',
    'augmented_assignment_expression',
    'update_expression',
    'reassignment',
}
_SCOPE_TYPES = {
    'program',
    'source_file',
    'module',
    'statement_block',
    'block',
    'function_body',
    'class_body',
}
_LITERAL_VALUE_TYPES = {
    'string',
    'string_literal',
    'interpreted_string_literal',
    'raw_string_literal',
    'line_string_literal',
    'number',
    'integer',
    'integer_literal',
    'decimal_integer_literal',
    'float',
    'float_literal',
    'true',
    'false',
    'boolean_literal',
    'null',
    'none',
    'nil',
    'object',
    'array',
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


def _enclosing_scope_span(node):
    """Return (start_byte, end_byte) of the nearest enclosing lexical scope."""
    cur = node.parent
    while cur is not None:
        if cur.type in _SCOPE_TYPES:
            return (cur.start_byte, cur.end_byte)
        cur = cur.parent
    return (0, 1 << 60)


def _is_const_declarator(node, source_bytes):
    """Return True if declarator node belongs to an immutable declaration."""
    if node.type == 'constant_declaration':
        return True
    if node.type not in _DECLARATOR_TYPES:
        return False
    parent = node.parent
    if parent is None:
        return False
    header = source_bytes[parent.start_byte:node.start_byte].strip()
    return header.startswith((b'const', b'val', b'final'))


def _declarator_pair(node, source_bytes):
    """Return (name_node, val_node) for an immutable single-line declarator."""
    if not _is_const_declarator(node, source_bytes):
        return None, None
    name_node = node.child_by_field_name(
        'name') or node.child_by_field_name('left')
    val_node = node.child_by_field_name(
        'value') or node.child_by_field_name('right')
    if name_node is None or val_node is None:
        return None, None
    if name_node.type not in _IDENTIFIER_TYPES:
        return None, None
    if val_node.type not in _LITERAL_VALUE_TYPES:
        return None, None
    if val_node.start_point[0] != val_node.end_point[0]:
        return None, None
    return name_node, val_node


def _collect_mutated_identifiers(root_node, source_bytes):
    """Return set of identifier byte strings that are reassigned/mutated."""
    mutated = set()
    stack = [root_node]
    while stack:
        node = stack.pop()
        if node.type in _MUTATION_TYPES:
            target = node.child_by_field_name(
                'left') or node.child_by_field_name('argument')
            if target is not None and target.type in _IDENTIFIER_TYPES:
                mutated.add(source_bytes[target.start_byte:target.end_byte])
        for child in node.children:
            if child.is_named:
                stack.append(child)
    return mutated


def _filter_unique_scope_bindings(bindings, counts):
    """Keep only bindings declared once in their enclosing scope."""
    clean = {}
    for ident, entries in bindings.items():
        valid = [
            e for e in entries
            if counts.get(((e[0], e[1]), ident), 0) == 1
        ]
        if valid:
            clean[ident] = valid
    return clean


def extract_scoped_constants(root_node, source_bytes):
    """Extract scope-aware immutable bindings: ident -> list of bindings."""
    mutated = _collect_mutated_identifiers(root_node, source_bytes)
    bindings = {}
    counts = {}
    stack = [root_node]
    while stack:
        node = stack.pop()
        name_node, val_node = _declarator_pair(node, source_bytes)
        if name_node is not None:
            ident = source_bytes[name_node.start_byte:name_node.end_byte]
            if ident and ident not in mutated:
                scope_span = _enclosing_scope_span(node)
                key = (scope_span, ident)
                counts[key] = counts.get(key, 0) + 1
                val_bytes = source_bytes[val_node.start_byte:val_node.end_byte]
                bindings.setdefault(ident, []).append(
                    (scope_span[0], scope_span[1], val_node.end_byte, val_bytes))
        for child in node.children:
            if child.is_named:
                stack.append(child)
    return _filter_unique_scope_bindings(bindings, counts)


def _resolve_scoped_value(ident, use_pos, scoped_consts):
    """Find the innermost in-scope constant value declared before use_pos."""
    candidates = scoped_consts.get(ident)
    if not candidates:
        return None
    best = None
    best_width = 1 << 62
    for s_start, s_end, decl_end, val_bytes in candidates:
        if s_start <= use_pos <= s_end and decl_end < use_pos:
            width = s_end - s_start
            if width < best_width:
                best_width = width
                best = val_bytes
    return best


def _is_non_value_identifier(node):
    """Return True if identifier node is a declaration LHS, callee, or key."""
    parent = node.parent
    if parent is None:
        return False
    for field in ('name', 'left', 'function', 'property', 'key'):
        if parent.child_by_field_name(field) == node:
            return True
    return False


def _collect_constant_replacements(root_node, source_bytes, scoped_consts):
    """Collect sorted (start, end, val_bytes) spans for identifier uses."""
    replacements = []
    stack = [root_node]
    while stack:
        node = stack.pop()
        if node.type in _IDENTIFIER_TYPES:
            ident = source_bytes[node.start_byte:node.end_byte]
            if ident in scoped_consts and not _is_non_value_identifier(node):
                val_bytes = _resolve_scoped_value(
                    ident, node.start_byte, scoped_consts)
                if val_bytes is not None:
                    replacements.append((
                        node.start_byte, node.end_byte, val_bytes))
            continue
        for child in node.children:
            if child.is_named:
                stack.append(child)
    replacements.sort(key=lambda item: item[0])
    return replacements


def inline_tree_constants(lang_name, tree, source_bytes):
    """Return (inlined_tree, offset_shifts) for constant-resolved matching."""
    scoped_consts = extract_scoped_constants(tree.root_node, source_bytes)
    if not scoped_consts:
        return tree, ()
    replacements = _collect_constant_replacements(
        tree.root_node, source_bytes, scoped_consts)
    if not replacements:
        return tree, ()
    out = bytearray()
    shifts = []
    cursor = 0
    cum_delta = 0
    for start, end, val_bytes in replacements:
        if start < cursor:
            continue
        out.extend(source_bytes[cursor:start])
        out.extend(val_bytes)
        new_end = len(out)
        cum_delta += len(val_bytes) - (end - start)
        shifts.append((new_end, cum_delta, start, end))
        cursor = end
    out.extend(source_bytes[cursor:])
    return parse_tree(lang_name, bytes(out)), tuple(shifts)


def _map_to_original_byte(inlined_byte, shifts, is_end=False):
    """Translate a byte offset from inlined source back to original source."""
    if not shifts:
        return inlined_byte
    ends = [s[0] for s in shifts]
    idx = bisect_right(ends, inlined_byte)
    if idx < len(shifts):
        new_end, _delta, orig_start, orig_end = shifts[idx]
        prev_delta = shifts[idx - 1][1] if idx > 0 else 0
        new_start = orig_start + prev_delta
        if new_start <= inlined_byte <= new_end:
            return orig_end if is_end else orig_start
        return inlined_byte - prev_delta
    return inlined_byte - shifts[-1][1]


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


def _ancestor_spans(lang_name, query_str, root_node):
    """Compute (start_byte, end_byte) spans for an ancestor query once."""
    if not query_str:
        return None
    q = get_compiled_query(lang_name, query_str)
    return [
        (a.start_byte, a.end_byte)
        for a in _captured_nodes(q, root_node)
    ]


def _in_spans(node, spans):
    """Return True if node is inside any (start, end) span."""
    if not spans:
        return False
    n_start, n_end = node.start_byte, node.end_byte
    return any(s <= n_start and n_end <= e for s, e in spans)


def _format_node_match(node, source_bytes, shifts=(), max_len=300):
    """Convert a matched AST Node into a libsast (match_str, pos, lines) tuple."""
    orig_start = _map_to_original_byte(node.start_byte, shifts, is_end=False)
    orig_end = max(
        orig_start,
        _map_to_original_byte(node.end_byte, shifts, is_end=True),
    )
    raw = source_bytes[orig_start:orig_end].decode('utf-8', 'ignore').strip()
    if max_len and len(raw) > max_len:
        raw = raw[:max_len]
    pos = (1 if orig_start == 0 else orig_start, orig_end)
    lines = (node.start_point[0] + 1, node.end_point[0] + 1)
    return (raw, pos, lines)


def _node_allowed(node, lang_name, excl_spans, within_spans, not_within):
    """Return True if node passes ancestor and not_within_node filters."""
    if excl_spans is not None and _in_spans(node, excl_spans):
        return False
    if within_spans is not None and not _in_spans(node, within_spans):
        return False
    if not_within and _matches_subquery(lang_name, not_within, node):
        return False
    return True


def find_query_matches(tree, source_bytes, lang_name, query_str, rule,
                       max_len=300, shifts=()):
    """Run a single S-expression query and return a set of formatted matches."""
    root = tree.root_node
    try:
        query = get_compiled_query(lang_name, query_str)
    except Exception:
        return set()
    captured = _captured_nodes(query, root)
    if not captured:
        return set()

    excl_spans = _ancestor_spans(lang_name, rule.get('exclude_ancestor'), root)
    within_spans = _ancestor_spans(lang_name, rule.get('within_ancestor'), root)
    not_within = rule.get('not_within_node')

    matches = set()
    for node in captured:
        if not _node_allowed(
                node, lang_name, excl_spans, within_spans, not_within):
            continue
        match_tuple = _format_node_match(node, source_bytes, shifts, max_len)
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
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len,
                        shifts=()):
        """Search for AST pattern matches in tree."""


class TreeSitter(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len,
                        shifts=()):
        patterns = rule['pattern']
        if isinstance(patterns, list):
            matches = set()
            for pat in patterns:
                matches.update(find_query_matches(
                    tree, source_bytes, lang_name, pat, rule, max_len, shifts))
            return matches
        return find_query_matches(
            tree, source_bytes, lang_name, patterns, rule, max_len, shifts)


class TreeSitterAnd(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len,
                        shifts=()):
        patterns = rule['pattern'] if isinstance(
            rule['pattern'], list) else [rule['pattern']]
        all_matches = set()
        for pat in patterns:
            matches = find_query_matches(
                tree, source_bytes, lang_name, pat, rule, max_len, shifts)
            if not matches:
                return False
            all_matches.update(matches)
        return all_matches


class TreeSitterOr(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len,
                        shifts=()):
        patterns = rule['pattern'] if isinstance(
            rule['pattern'], list) else [rule['pattern']]
        matches = set()
        for pat in patterns:
            matches.update(find_query_matches(
                tree, source_bytes, lang_name, pat, rule, max_len, shifts))
        return matches


class TreeSitterAndNot(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len,
                        shifts=()):
        present_pat, absent_pat = rule['pattern']
        absent_matches = find_query_matches(
            tree, source_bytes, lang_name, absent_pat, {}, max_len, shifts)
        if absent_matches:
            return False
        present_matches = find_query_matches(
            tree, source_bytes, lang_name, present_pat, rule, max_len, shifts)
        return present_matches if present_matches else False


class TreeSitterAndOr(TSMatchStrategy):
    def _perform_search(self, tree, source_bytes, lang_name, rule, max_len,
                        shifts=()):
        and_pat, or_pats = rule['pattern']
        and_matches = find_query_matches(
            tree, source_bytes, lang_name, and_pat, rule, max_len, shifts)
        if not and_matches:
            return False
        for pat in or_pats:
            or_matches = find_query_matches(
                tree, source_bytes, lang_name, pat, rule, max_len, shifts)
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
