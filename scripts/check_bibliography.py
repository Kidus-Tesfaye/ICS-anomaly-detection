"""Validate the project bibliography exported from Zotero.

The ``.bib`` file is a *generated artifact* (exported from Zotero), so it can silently
regress whenever it is re-exported: entries lose fields, duplicates creep in, or the
export dialect changes. This script makes those regressions visible and reproducible
instead of something a human has to spot by eye.

It checks:

* **Dialect consistency** - BibTeX (``journal``/``year``) vs BibLaTeX
  (``journaltitle``/``date``). A file that mixes both usually means the wrong Zotero
  exporter was chosen; the two dialects need different LaTeX toolchains
  (``bibtex`` vs ``biber``), so the choice must be deliberate.
* **Required fields** - author, title, and a venue for peer-reviewed entry types.
* **Duplicates** - repeated citation keys, and near-identical titles that indicate the
  same work imported twice (e.g. a preprint and its published version).
* **Traceability** - a DOI or URL, and an attached PDF, so every claim in the review
  can be checked against the source.
* **Preprint-only citations** - flagged so they are a deliberate choice, not an oversight.

Usage::

    python scripts/check_bibliography.py                  # default path, warnings allowed
    python scripts/check_bibliography.py --strict         # warnings also fail
    python scripts/check_bibliography.py path/to/file.bib

Exit code is 0 when no errors are found, 1 otherwise, so this can be wired into CI.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_BIB = Path(__file__).resolve().parents[1] / "docs" / "ICS Anomaly Detection.bib"

# Entry types that are not peer-reviewed literature: they are allowed to lack a venue,
# a date, and an attached PDF.
NON_LITERATURE_TYPES = frozenset({"online", "misc", "software", "dataset", "manual", "techreport"})

# Field names that identify each dialect. Zotero's "Better BibTeX" exporter emits the
# first set; "Better BibLaTeX" emits the second.
BIBTEX_FIELDS = ("journal", "year", "address")
BIBLATEX_FIELDS = ("journaltitle", "date", "location", "eventtitle")

VENUE_FIELDS = ("journaltitle", "journal", "booktitle", "publisher", "organization", "institution")
DATE_FIELDS = ("date", "year")


@dataclass
class Entry:
    """One parsed bibliography entry."""

    key: str
    type: str
    fields: dict[str, str]
    line: int

    def get(self, *names: str) -> str:
        """Return the first non-empty value among ``names`` (dialect-agnostic lookup)."""
        for name in names:
            value = self.fields.get(name.lower(), "")
            if value:
                return value
        return ""

    @property
    def is_literature(self) -> bool:
        return self.type not in NON_LITERATURE_TYPES

    @property
    def year(self) -> str:
        return self.get(*DATE_FIELDS)[:4]

    @property
    def has_pdf(self) -> bool:
        return ".pdf" in self.get("file").lower()

    @property
    def is_preprint_only(self) -> bool:
        """True when the entry cites a preprint and names no peer-reviewed venue.

        An entry that has *both* an arXiv eprint and a real venue is good practice - the
        published version is cited, and the eprint gives readers a free copy - so it is
        deliberately not flagged here.
        """
        if "prepublished" in self.get("pubstate").lower():
            return True
        looks_like_eprint = "arxiv" in f"{self.get('eprinttype')} {self.get('url')}".lower()
        return looks_like_eprint and not self.get("journaltitle", "journal", "booktitle")


@dataclass
class Report:
    """Accumulated findings, split by severity."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)


def parse_bib(text: str) -> list[Entry]:
    """Parse ``.bib`` text into entries.

    Deliberately a small hand-rolled parser rather than a dependency: it only needs to
    read fields, and keeping it dependency-free means the check runs anywhere the repo
    is installed. Brace depth is tracked so nested braces inside values (common in
    Zotero's case-protected titles, e.g. ``{{SWaT}}``) do not terminate a field early.
    """
    entries: list[Entry] = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        entry_type, key = match.group(1).lower(), match.group(2)
        line = text.count("\n", 0, match.start()) + 1

        # Walk forward from the entry header to its matching closing brace.
        depth, end = 1, match.end()
        for index in range(match.end(), len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = index
                    break
        else:
            end = len(text)

        entries.append(
            Entry(key=key, type=entry_type, fields=parse_fields(text[match.end() : end]), line=line)
        )
    return entries


def parse_fields(body: str) -> dict[str, str]:
    """Extract ``name = {value}`` and ``name = "value"`` pairs from an entry body."""
    fields: dict[str, str] = {}
    for match in re.finditer(r"(\w+)\s*=\s*", body):
        name = match.group(1).lower()
        rest = body[match.end() :].lstrip()
        if not rest:
            continue
        if rest[0] == "{":
            depth, chars = 1, []
            for char in rest[1:]:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        break
                chars.append(char)
            value = "".join(chars)
        elif rest[0] == '"':
            value = rest[1:].split('"', 1)[0]
        else:
            value = rest.split(",", 1)[0]
        fields[name] = re.sub(r"\s+", " ", value).strip()
    return fields


def normalize_title(title: str) -> str:
    """Reduce a title to a comparable form so near-duplicates collide."""
    return re.sub(r"[^a-z0-9]+", "", title.lower())[:70]


def check_dialect(entries: list[Entry], report: Report) -> None:
    """Warn when the file mixes BibTeX and BibLaTeX field conventions."""
    bibtex = sum(bool(e.get(*BIBTEX_FIELDS)) for e in entries)
    biblatex = sum(bool(e.get(*BIBLATEX_FIELDS)) for e in entries)
    if not (bibtex or biblatex):
        return

    if biblatex and bibtex:
        dominant = "BibLaTeX" if biblatex >= bibtex else "BibTeX"
        report.warn(
            f"Mixed dialects: {biblatex} entries use BibLaTeX fields "
            f"(journaltitle/date/location), {bibtex} use BibTeX fields (journal/year). "
            f"The file is predominantly {dominant}. Re-export from Zotero choosing ONE "
            f"exporter: 'Better BibTeX' for bibtex/IEEEtran, 'Better BibLaTeX' for biber."
        )
    else:
        name = "BibLaTeX" if biblatex else "BibTeX"
        engine = "biber + \\usepackage{biblatex}" if biblatex else "bibtex + \\bibliographystyle"
        report.note(f"Dialect: {name} (requires {engine})")


def check_entry(entry: Entry, report: Report) -> None:
    """Apply per-entry field requirements."""
    where = f"{entry.key} (line {entry.line})"

    if not entry.get("title"):
        report.error(f"{where}: missing title")
    if not entry.get("author", "editor"):
        report.error(f"{where}: missing author/editor")

    if entry.is_literature:
        if not entry.get(*VENUE_FIELDS):
            report.error(f"{where}: missing venue (journal/booktitle/publisher)")
        if not entry.year:
            report.error(f"{where}: missing year")
        if not entry.has_pdf:
            report.warn(f"{where}: no PDF attached - cannot verify claims against source")

    if not entry.get("doi") and not entry.get("url"):
        report.warn(f"{where}: no DOI or URL - reader cannot locate this source")

    if entry.is_preprint_only:
        report.note(f"{where}: preprint only, no peer-reviewed venue - confirm this is deliberate")


def check_duplicates(entries: list[Entry], report: Report) -> None:
    """Detect repeated citation keys and near-identical titles."""
    for key, count in Counter(e.key for e in entries).items():
        if count > 1:
            report.error(f"duplicate citation key '{key}' appears {count} times")

    by_title: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        if title := normalize_title(entry.get("title")):
            by_title[title].append(entry.key)
    for keys in by_title.values():
        if len(keys) > 1:
            report.error(f"duplicate/near-duplicate titles: {', '.join(keys)}")


def build_report(entries: list[Entry]) -> Report:
    report = Report()
    check_dialect(entries, report)
    check_duplicates(entries, report)
    for entry in entries:
        check_entry(entry, report)
    return report


def print_report(entries: list[Entry], report: Report, path: Path) -> None:
    counts = Counter(e.type for e in entries)
    literature = sum(e.is_literature for e in entries)

    print(f"Bibliography: {path}")
    print(f"  {len(entries)} entries ({literature} literature, {len(entries) - literature} other)")
    print("  " + ", ".join(f"@{t}={c}" for t, c in counts.most_common()))

    for label, items in (
        ("ERROR", report.errors),
        ("WARN", report.warnings),
        ("NOTE", report.notes),
    ):
        if items:
            print(f"\n{label} ({len(items)}):")
            for item in items:
                print(f"  - {item}")

    if not report.errors:
        print("\nNo errors.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "bib", nargs="?", type=Path, default=DEFAULT_BIB, help="path to the .bib file"
    )
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors (for CI use)"
    )
    args = parser.parse_args(argv)

    if not args.bib.is_file():
        print(f"error: no such file: {args.bib}", file=sys.stderr)
        return 2

    entries = parse_bib(args.bib.read_text(encoding="utf-8", errors="replace"))
    if not entries:
        print(f"error: no entries parsed from {args.bib}", file=sys.stderr)
        return 2

    report = build_report(entries)
    print_report(entries, report, args.bib)

    failed = bool(report.errors) or (args.strict and bool(report.warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
