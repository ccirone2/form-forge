#!/usr/bin/env python3
"""Sync embedded documentation constants in index.html from doc source files.

Usage:
    python scripts/sync-embedded-docs.py          # update index.html in place
    python scripts/sync-embedded-docs.py --check  # CI: exit 1 if out of sync
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"

DOCS = {
    "SCHEMA_GUIDE": REPO_ROOT / "docs" / "SCHEMA_GUIDE.md",
    "TEMPLATE_GUIDE": REPO_ROOT / "docs" / "TEMPLATE_GUIDE.md",
    "FIELD_TYPES": REPO_ROOT / "docs" / "FIELD_TYPES.md",
}


def escape_for_template_literal(text: str) -> str:
    """Escape a string for safe embedding inside JS backtick template literals."""
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def build_block(name: str, content: str) -> str:
    """Build the full EMBEDDED-DOC marker block for a given doc constant."""
    escaped = escape_for_template_literal(content)
    return (
        f"// EMBEDDED-DOC:{name}:START\n"
        f"const DOCS_{name} = `{escaped}`;\n"
        f"// EMBEDDED-DOC:{name}:END"
    )


def main() -> int:
    """Entry point: sync or check embedded doc constants in index.html."""
    check_mode = "--check" in sys.argv

    if not INDEX_HTML.exists():
        print(f"ERROR: {INDEX_HTML} not found", file=sys.stderr)
        return 1

    html = INDEX_HTML.read_text(encoding="utf-8")
    new_html = html

    for name, path in DOCS.items():
        if not path.exists():
            print(f"ERROR: {path} not found", file=sys.stderr)
            return 1

        content = path.read_text(encoding="utf-8")
        replacement = build_block(name, content)

        pattern = re.compile(
            r"// EMBEDDED-DOC:" + re.escape(name) + r":START\n"
            r".*?"
            r"// EMBEDDED-DOC:" + re.escape(name) + r":END",
            re.DOTALL,
        )

        if not pattern.search(new_html):
            print(f"ERROR: marker block for {name} not found in index.html", file=sys.stderr)
            return 1

        # Use lambda to avoid re.sub interpreting backslashes in replacement
        new_html = pattern.sub(lambda _: replacement, new_html)

    if check_mode:
        if new_html != html:
            print(
                "ERROR: Embedded docs are out of sync. Run: python scripts/sync-embedded-docs.py",
                file=sys.stderr,
            )
            return 1
        print("OK: Embedded docs are in sync.")
        return 0

    if new_html != html:
        INDEX_HTML.write_text(new_html, encoding="utf-8")
        print("Updated embedded docs in index.html.")
    else:
        print("Embedded docs already in sync.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
