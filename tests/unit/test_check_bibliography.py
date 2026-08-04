"""Tests for the bibliography validator in scripts/check_bibliography.py.

The script lives in scripts/ rather than src/, so it is loaded here by path. Each test
feeds a tiny hand-written .bib snippet and asserts on the findings, which keeps them
fast and independent of the real (Zotero-generated) bibliography.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_bibliography.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_bibliography", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cb = load_script()

COMPLETE = """
@inproceedings{goodEntry2020,
  title = {A {{Complete}} Entry},
  booktitle = {Proceedings of Somewhere},
  author = {Doe, Jane and Roe, Richard},
  date = {2020-05-01},
  doi = {10.1000/xyz},
  file = {C:\\Zotero\\storage\\AAA\\paper.pdf}
}
"""


def findings(text: str) -> cb.Report:
    return cb.build_report(cb.parse_bib(text))


def test_complete_entry_has_no_findings() -> None:
    report = findings(COMPLETE)
    assert report.errors == []
    assert report.warnings == []


def test_parses_key_type_and_fields() -> None:
    (entry,) = cb.parse_bib(COMPLETE)
    assert entry.key == "goodEntry2020"
    assert entry.type == "inproceedings"
    assert entry.get("author") == "Doe, Jane and Roe, Richard"
    assert entry.year == "2020"
    assert entry.has_pdf


def test_nested_braces_do_not_truncate_values() -> None:
    """Zotero case-protects titles as {{SWaT}}; the parser must keep the whole value."""
    (entry,) = cb.parse_bib("@article{k, title = {{{SWaT}}: A {{Testbed}} Study}, }")
    assert entry.get("title") == "{{SWaT}}: A {{Testbed}} Study"


@pytest.mark.parametrize(
    ("field_name", "expected"),
    [("author", "missing author/editor"), ("title", "missing title")],
)
def test_missing_required_fields_are_errors(field_name: str, expected: str) -> None:
    stripped = "\n".join(
        line for line in COMPLETE.splitlines() if not line.strip().startswith(f"{field_name} =")
    )
    assert any(expected in e for e in findings(stripped).errors)


def test_missing_venue_is_error_for_literature_but_not_for_online() -> None:
    no_venue = "@article{a, title = {T}, author = {A}, date = {2020}}"
    assert any("missing venue" in e for e in findings(no_venue).errors)

    online = "@online{b, title = {T}, author = {{Org}}, url = {https://example.org}}"
    assert findings(online).errors == []


def test_duplicate_keys_and_titles_are_errors() -> None:
    same_key = COMPLETE + COMPLETE
    assert any("duplicate citation key" in e for e in findings(same_key).errors)

    same_title = COMPLETE + COMPLETE.replace("goodEntry2020", "otherKey2021")
    assert any("near-duplicate titles" in e for e in findings(same_title).errors)


def test_missing_doi_and_pdf_are_warnings_not_errors() -> None:
    minimal = "@article{a, title = {T}, author = {A}, date = {2020}, journaltitle = {J}}"
    report = findings(minimal)
    assert report.errors == []
    assert any("no DOI or URL" in w for w in report.warnings)
    assert any("no PDF attached" in w for w in report.warnings)


def test_preprint_with_published_venue_is_not_flagged() -> None:
    """An arXiv eprint alongside a real venue is good practice, not a problem."""
    both = """
    @inproceedings{k, title = {T}, author = {A}, date = {2023},
      booktitle = {Proceedings of KDD}, eprinttype = {arXiv}, eprint = {2306.10347},
      file = {a.pdf}}
    """
    assert not [n for n in findings(both).notes if "preprint" in n]

    preprint_only = """
    @article{k, title = {T}, author = {A}, date = {2023},
      journaltitle = {J}, pubstate = {prepublished}, doi = {10.1/x}, file = {a.pdf}}
    """
    assert any("preprint only" in n for n in findings(preprint_only).notes)


def test_mixed_dialects_produce_a_warning() -> None:
    mixed = """
    @article{a, title = {T}, author = {A}, journaltitle = {J}, date = {2020},
      doi = {1}, file = {a.pdf}}
    @article{b, title = {U}, author = {B}, journal = {J}, year = {2021},
      doi = {2}, file = {b.pdf}}
    """
    assert any("Mixed dialects" in w for w in findings(mixed).warnings)


def test_main_exit_codes(tmp_path: Path) -> None:
    good = tmp_path / "good.bib"
    good.write_text(COMPLETE, encoding="utf-8")
    assert cb.main([str(good)]) == 0

    bad = tmp_path / "bad.bib"
    bad.write_text("@article{a, title = {T}}", encoding="utf-8")
    assert cb.main([str(bad)]) == 1

    assert cb.main([str(tmp_path / "missing.bib")]) == 2
