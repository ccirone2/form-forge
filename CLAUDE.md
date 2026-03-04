# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FormForge is a **client-side-only** browser application that turns GitHub-hosted JSON schemas into dynamic HTML forms and exports filled data as DOCX documents via Pyodide (Python in WebAssembly). No server, no database — GitHub is the CMS.

**Data flow:** GitHub repo → fetch schema JSON + template .py → render form in browser → user fills form → Pyodide runs template → DOCX downloads locally.

## Architecture

- **`index.html`** — The entire frontend: HTML + CSS + JS in one file (~2400 lines). Contains the form builder, GitHub API integration, Pyodide loader, validation, and UI. Do not split this file unless the expansion guide explicitly calls for it.
- **`schemas/_schema.spec.json`** — JSON Schema (draft 2020-12) that validates all form schemas. Enforces required fields, valid field types (17 enumerated), conditional constraints (e.g., `select` requires `options`, `repeater` requires `fields`), and `additionalProperties: false` at all levels.
- **`schemas/*.json`** — Form definitions. Each schema has `title`, `description`, `icon`, `template` (path to .py), and `sections[]` containing `fields[]` with `id`, `label`, `type`, etc.
- **`templates/_base.py`** — Shared helper module for all templates. Provides `new_doc()`, `add_table_section()`, `add_longtext()`, `add_bullet_list()`, `add_signatures()`, `finalize()`, and a standard color palette. Loaded into Pyodide's virtual filesystem once via `loadBaseModule()` before any template runs.
- **`templates/*.py`** — Python scripts that export a `generate_docx(data)` function. Called by Pyodide with form data as a dict. Must return DOCX bytes. Uses `python-docx` and `import _base`.
- **`docs/FORMFORGE_EXPANSION_GUIDE.md`** — Project roadmap and architectural reference. Consult before making design decisions.
- **`docs/DEVLOG.md`** — Running development journal. Add a dated entry when completing work on any issue.
- **`docs/SCHEMA_GUIDE.md`** — Guide for writing new form schemas.
- **`docs/TEMPLATE_GUIDE.md`** — Guide for writing new Python templates.
- **`docs/FIELD_TYPES.md`** — Reference for all 17 supported field types, their JSON schema, and template handling.

## Pyodide Integration

`index.html` manages the Pyodide lifecycle:

1. `initPyodide()` — Loads Pyodide from CDN, installs `python-docx` via micropip
2. `loadBaseModule()` — Fetches `_base.py` (from connected repo or FormForge repo), writes it to Pyodide's virtual filesystem via `pyodide.FS.writeFile()`, then runs `import _base`. Executes once per session (cached via `baseModuleLoaded` flag, reset on repo change).
3. `pyodide.runPythonAsync(templateCode)` — Loads the template
4. `generate_docx(form_data)` — Called via `runPythonAsync` with serialized form data

There are 4 template loading paths that all follow this pattern: `launchForm()` (GitHub), its override (GitHub picker), `launchLocal()` (local files), and `launchDemo()` (embedded demo).

## Key Conventions

- **Default branch is `develop`**, not main. Feature branches: `feature/ISSUE-NUMBER-short-description`.
- **Stay client-side.** Every feature must work with zero infrastructure. No servers, no build steps.
- **Templates are standalone Python.** They must work both in Pyodide and in a normal Python environment (for testing).
- **Templates use `_base` helpers.** New templates should `import _base` and use shared utilities rather than duplicating code.
- **Schema field IDs** follow the pattern `^[a-z][a-z0-9_]*$`.
- **`generate_docx(data)`** is the required entry point for all templates. `data` is a dict keyed by field `id`. All values are strings (complex types like address/repeater are JSON strings).
- The HTML app fetches schemas/templates from GitHub via the public API — file paths in schemas (e.g., `"template": "templates/onboarding.py"`) are relative to the repo root.
- Adding a new field type touches three places: `createField()` switch in index.html, `collectFormData()` in index.html, and the template .py file.

## Development

No build system or package manager. Pyodide and python-docx load from CDN at runtime.

```bash
# Run locally — open index.html directly or use HTTP server for CORS
python -m http.server 8000

# Run all tests (33 tests)
PYTHONPATH=. python -m pytest tests/ -v

# Run a single test file
PYTHONPATH=. python -m pytest tests/test_base.py -v

# Run a single test
PYTHONPATH=. python -m pytest tests/test_base.py::test_new_doc_creates_document -v

# Lint
ruff check templates/ tests/ --fix
ruff format templates/ tests/
```

### Test structure

- `tests/test_base.py` — Unit tests for all `_base.py` utilities (14 tests)
- `tests/test_templates.py` — Integration tests that load each template with sample data and verify valid DOCX output (4 tests)
- `tests/test_schemas.py` — Schema validation tests: validates all schemas against `_schema.spec.json`, plus negative tests for invalid schemas (15 tests)
- `tests/fixtures/*.json` — Sample form data matching each schema's field IDs
- Templates are loaded via `importlib.util.spec_from_file_location()` with `sys.path` including `templates/` so `import _base` resolves

## GitHub Issues

Each issue includes a journaling task to update `docs/DEVLOG.md`.
