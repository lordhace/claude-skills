#!/usr/bin/env python3
"""
Generate an Azure DevOps Test Plan-importable CSV from a structured test-case spec.

This script exists so the *formatting* is deterministic and correct every time:
the 11-column layout, the header-row vs. step-row split, and the exact quoting
rules. The thinking part (reading the JIRA Acceptance Criteria and deciding what
the test cases and steps should be) is done by Claude and handed to this script
as JSON.

Before writing anything, the script also rejects duplicate/repeating test
cases: two test cases with the same title, or two with different titles but
an identical step-by-step script. This is a backstop, not the primary
defense — the spec should already be duplicate-free when it's written (see
the skill's "Design the test cases" step); the check just guarantees a
duplicate can never silently make it into the CSV.

Input JSON shape:
{
  "test_cases": [
    {
      "title": "Verify ...",                     # written verbatim, no TC- prefix
      "steps": [
        {"action": "...", "expected": "..."},
        ...
      ]
    },
    ...
  ],
  # optional overrides for the standard field values:
  "fields": {
    "state": "Design",
    "assigned_to": "Leochard Catipay",
    "area": "Clockworks Applications",
    "iteration_path": "Clockworks Applications\\Software 09-09-26 to 09-29-26",
    "tags": "TBD"
  }
}

Usage:
    python generate_csv.py input.json [output.csv]
If output path is omitted, prints to stdout.
"""

import json
import sys

COLUMNS = [
    "ID",
    "Work Item Type",
    "Title",
    "State",
    "Assigned To",
    "Area",
    "Iteration Path",
    "Tags",
    "Test Step",
    "Step Action",
    "Step Expected",
]

DEFAULT_FIELDS = {
    "state": "Design",
    "assigned_to": "Leochard Catipay",
    "area": "Clockworks Applications",
    "iteration_path": "Clockworks Applications\\Software 09-09-26 to 09-29-26",
    "tags": "TBD",
}

# Characters that force a field to be quoted.
# QUOTE_MINIMAL: a comma triggers quoting. We also force-quote on pipe "|"
# (ADO treats it specially) and on the CSV-structural characters " and newlines.
_QUOTE_TRIGGERS = (",", "|", '"', "\n", "\r")


def quote_field(value: str) -> str:
    """Quote a single field only when it contains a trigger char (QUOTE_MINIMAL + pipe)."""
    s = "" if value is None else str(value)
    if any(ch in s for ch in _QUOTE_TRIGGERS):
        return '"' + s.replace('"', '""') + '"'
    return s


def make_row(values):
    """Build one CSV line from exactly 11 raw field values."""
    if len(values) != len(COLUMNS):
        raise ValueError(
            f"Row has {len(values)} columns, expected {len(COLUMNS)}: {values!r}"
        )
    return ",".join(quote_field(v) for v in values)


def _normalize(text):
    """Lowercase + collapse whitespace, for duplicate comparison only (not output)."""
    return " ".join(("" if text is None else str(text)).split()).casefold()


def find_duplicates(spec):
    """Detect duplicate/repeating test cases before any CSV is written.

    Two kinds of duplication are caught:
    - duplicate_titles: two or more test cases with the same title (after
      trimming/whitespace-collapsing/case-folding) — almost always a copy-paste
      or re-run artifact.
    - duplicate_scripts: two or more test cases whose full step sequence
      (every action + expected pair, in order) is identical even though the
      titles differ — the same test case restated under a different name.

    Returns a dict: {"duplicate_titles": [...], "duplicate_scripts": [...]}
    where each entry is {"key": <normalized value>, "titles": [original titles]}.
    Empty lists mean no duplicates found.
    """
    by_title = {}
    by_script = {}

    for tc in spec.get("test_cases", []):
        title = tc.get("title", "").strip()
        title_key = _normalize(title)
        by_title.setdefault(title_key, []).append(title)

        script_key = tuple(
            (_normalize(s.get("action")), _normalize(s.get("expected")))
            for s in tc.get("steps", [])
        )
        # Only treat a shared script as a duplicate if it actually has steps —
        # two empty-step test cases aren't meaningfully "the same test".
        if script_key:
            by_script.setdefault(script_key, []).append(title)

    duplicate_titles = [
        {"key": k, "titles": v} for k, v in by_title.items() if len(v) > 1
    ]
    duplicate_scripts = [
        {"key": k, "titles": v} for k, v in by_script.items() if len(v) > 1
    ]
    return {"duplicate_titles": duplicate_titles, "duplicate_scripts": duplicate_scripts}


def build_rows(spec):
    fields = dict(DEFAULT_FIELDS)
    fields.update(spec.get("fields", {}))

    rows = [list(COLUMNS)]  # column header row

    for tc in spec.get("test_cases", []):
        title = tc.get("title", "").strip()
        # TC header row: ID empty, Work Item Type = Test Case, Title + metadata filled,
        # last 3 (Test Step, Step Action, Step Expected) empty.
        rows.append([
            "",                       # ID
            "Test Case",              # Work Item Type
            title,                    # Title
            fields["state"],          # State
            fields["assigned_to"],    # Assigned To
            fields["area"],           # Area
            fields["iteration_path"], # Iteration Path
            fields["tags"],           # Tags
            "", "", "",               # Test Step, Step Action, Step Expected
        ])

        # Step rows: first 8 fields empty, then step number, action, expected.
        for i, step in enumerate(tc.get("steps", []), start=1):
            rows.append([
                "", "", "", "", "", "", "", "",   # 8 leading empty fields
                str(i),                           # Test Step (number)
                step.get("action", ""),           # Step Action
                step.get("expected", ""),         # Step Expected
            ])

    return rows


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        spec = json.load(f)

    # Fail before writing anything if the spec contains duplicate or
    # repeating test cases — see find_duplicates() for what counts.
    dupes = find_duplicates(spec)
    if dupes["duplicate_titles"] or dupes["duplicate_scripts"]:
        lines = ["Duplicate test cases found — fix the spec and re-run:"]
        for d in dupes["duplicate_titles"]:
            lines.append(f'  - Repeated title ({len(d["titles"])}x): "{d["titles"][0]}"')
        for d in dupes["duplicate_scripts"]:
            titles = ", ".join(f'"{t}"' for t in d["titles"])
            lines.append(f"  - Identical step sequence under different titles: {titles}")
        raise SystemExit("\n".join(lines))

    rows = build_rows(spec)

    # Verify every row is exactly 11 columns before emitting.
    for idx, r in enumerate(rows):
        if len(r) != len(COLUMNS):
            raise SystemExit(f"Row {idx} has {len(r)} columns, expected 11.")

    output = "\r\n".join(make_row(r) for r in rows) + "\r\n"

    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8", newline="") as f:
            f.write(output)
        print(f"Wrote {len(rows)} rows ({len(rows) - 1} data rows) to {sys.argv[2]}")
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
