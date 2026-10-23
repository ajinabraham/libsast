"""Tests for SemanticGrep input filtering."""
from pathlib import Path

from libsast.core_sgrep.semantic_sgrep import SemanticGrep


def test_scan_skips_semgrep_when_no_paths_match_requested_extensions(monkeypatch):
    invoked = []

    def fake_invoke_semgrep(paths, rules):
        invoked.append((paths, rules))
        return {"results": [], "errors": []}

    monkeypatch.setattr(
        "libsast.core_sgrep.semantic_sgrep.invoke_semgrep", fake_invoke_semgrep
    )
    scanner = SemanticGrep(
        {"sgrep_rules": "synthetic-rules", "sgrep_extensions": [".py"]}
    )

    result = scanner.scan([Path("synthetic-benign.txt")])

    assert invoked == []
    assert result == {"matches": {}, "errors": []}


def test_scan_only_passes_matching_extensions_to_semgrep(monkeypatch):
    invoked = []

    def fake_invoke_semgrep(paths, rules):
        invoked.append((paths, rules))
        return {"results": [], "errors": []}

    monkeypatch.setattr(
        "libsast.core_sgrep.semantic_sgrep.invoke_semgrep", fake_invoke_semgrep
    )
    scanner = SemanticGrep(
        {"sgrep_rules": "synthetic-rules", "sgrep_extensions": [".py"]}
    )
    paths = [Path("synthetic-benign.txt"), Path("synthetic-benign.py")]

    scanner.scan(paths)

    assert invoked == [([Path("synthetic-benign.py")], "synthetic-rules")]
