# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FormForge is a **client-side-only** browser application that turns GitHub-hosted JSON schemas into dynamic HTML forms and exports filled data as DOCX documents via Pyodide (Python in WebAssembly). No server, no database — GitHub is the CMS.

**Data flow:** GitHub repo → fetch schema JSON + template .py → render form in browser → user fills form → Pyodide runs template → DOCX downloads locally.

## Architecture

- **`index.html`** — The entire frontend: HTML + CSS + JS in one file (~1900 lines). Contains the form builder, GitHub API integration, Pyodide loader, validation, and UI. Do not split this file unless the expansion guide explicitly calls for it.
- **`schemas/*.json`** — Form definitions. Each schema has `title`, `description`, `icon`, `template` (path to .py), and `sections[]` containing `fields[]` with `id`, `label`, `type`, etc.
- **`templates/*.py`** — Python scripts that export a `generate_docx(data)` function. Called by Pyodide with form data as a dict. Must return DOCX bytes. Uses `python-docx`.
- **`docs/FORMFORGE_EXPANSION_GUIDE.md`** — Project roadmap and architectural reference. Consult before making design decisions.
- **`docs/DEVLOG.md`** — Running development journal. Add a dated entry when completing work on any issue.
- **`docs/SCHEMA_GUIDE.md`** — Guide for writing new form schemas.
- **`docs/TEMPLATE_GUIDE.md`** — Guide for writing new Python templates.

## Supported Field Types

- **`docs/FIELD_TYPES.md`** — Reference for all supported form field types, their JSON schema, and template handling.

Adding a new type touches three places: `createField()` switch in index.html, `collectFormData()` in index.html, and the template .py file.

## Key Conventions

- **Default branch is `develop`**, not main.
- **Stay client-side.** Every feature must work with zero infrastructure. No servers, no build steps.
- **Templates are standalone Python.** They must work both in Pyodide and in a normal Python environment (for testing).
- **Schema field IDs** follow the pattern `^[a-z][a-z0-9_]*$`.
- **`generate_docx(data)`** is the required entry point for all templates. `data` is a dict keyed by field `id`.
- The HTML app fetches schemas/templates from GitHub via the public API — file paths in schemas (e.g., `"template": "templates/onboarding.py"`) are relative to the repo root.

## Development

No build system or package manager is configured yet. To work on this project:

- **Run locally:** Open `index.html` in a browser (or use a local HTTP server for CORS). Pyodide loads from CDN.
- **Test templates standalone:** `pip install python-docx` then run a template directly with sample data.
- **Validate schemas:** Once `schemas/_schema.spec.json` exists (issue #4), use `jsonschema` to validate.

## GitHub Issues

Each issue includes a journaling task to update `docs/DEVLOG.md`.
