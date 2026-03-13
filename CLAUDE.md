# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FormForge is a **client-side-only** browser application that turns GitHub-hosted JSON schemas into dynamic HTML forms and exports filled data as DOCX documents via Pyodide (Python in WebAssembly). No server, no database — GitHub is the CMS.

**Data flow:** GitHub repo → fetch schema JSON + template .py → render form in browser → user fills form → Pyodide runs template → DOCX downloads locally.

## Architecture

- **`index.html`** — The entire frontend: HTML + CSS + JS in one file (~4600 lines). Contains the form builder, GitHub API integration, Pyodide loader, validation, and UI. Do not split this file.
- **`schemas/_schema.spec.json`** — JSON Schema (draft 2020-12) that validates all form schemas. Enforces required fields, valid field types (18 enumerated), conditional constraints (e.g., `select` requires `options`, `repeater` requires `fields`), and `additionalProperties: false` at all levels.
- **`schemas/*.json`** — Form definitions. Each schema has `title`, `description`, `icon`, `template` (path to .py), and `sections[]` containing `fields[]` with `id`, `label`, `type`, etc.
- **`templates/stencils.py`** — Shared helper module for all templates. Provides `set_theme()`, `new_doc()`, `table_section()`, `longtext()`, `bullet_list()`, `signatures()`, `footer()`, `address()`, `image()`, `signature()`, `repeater_table()`, `finalize()`, and a `DocTheme` system with built-in themes (`THEME_CLASSIC`, `THEME_MINIMAL`, `THEME_MODERN`). Loaded into Pyodide's virtual filesystem once via `loadBaseModule()` before any template runs.
- **`templates/*.py`** — Python scripts that export a `generate_docx(data)` function. Called by Pyodide with form data as a dict. Must return DOCX bytes. Uses `python-docx` and `import stencils`.
- **`docs/DEVLOG.md`** — Running development journal. Add a dated entry when completing work on any issue.
- **`docs/SCHEMA_GUIDE.md`** — Guide for writing new form schemas.
- **`docs/TEMPLATE_GUIDE.md`** — Guide for writing new Python templates.
- **`docs/FIELD_TYPES.md`** — Reference for all 18 supported field types, their JSON schema, and template handling.
- **`docs/PLAN.md`** — Structured implementation plans for upcoming features.

## Pyodide Integration

`index.html` manages the Pyodide lifecycle:

1. `initPyodide()` — Loads Pyodide from CDN, installs `python-docx` via micropip
2. `loadBaseModule()` — Fetches `stencils.py` (from connected repo or FormForge repo), writes it to Pyodide's virtual filesystem via `pyodide.FS.writeFile()`, then runs `import stencils`. Executes once per session (cached via `baseModuleLoaded` flag, reset on repo change).
3. `pyodide.runPythonAsync(templateCode)` — Loads the template
4. `generate_docx(form_data)` — Called via `runPythonAsync` with serialized form data

There are 3 template loading paths that all follow this pattern: `launchForm()` (GitHub), `launchLocal()` (local files), and `launchDemo()` (embedded demo).

### Wizard Form Support

Schemas with `"wizard": true` render as multi-step forms instead of all-at-once. Each section gets an optional `"step"` (positive integer ≥1). The UI shows a step indicator (numbered circles + connectors), displays one section at a time, and validates per-step before advancing via `wizardValidateStep()`. Submit is only available on the final step. Data is preserved across step navigation.

### Conditional Field Visibility (`visible_when`)

Fields can have an optional `visible_when` object: `{ "field": "<source_id>", "equals": "<value>" }`. When the source field's value doesn't match, the dependent field is hidden (CSS class `conditional-hidden`). `setupConditionalVisibility(schema)` builds the dependency map and attaches listeners. Hidden fields are skipped during validation but still collected as empty strings in `collectFormData()`.

## Key Conventions

- **Default branch is `develop`**, not main. Feature branches: `feature/ISSUE-NUMBER-short-description`.
- **Stay client-side.** Every feature must work with zero infrastructure. No servers, no build steps.
- **Templates are standalone Python.** They must work both in Pyodide and in a normal Python environment (for testing).
- **Templates use `stencils` helpers.** New templates should `import stencils` and use shared utilities rather than duplicating code.
- **Schema field IDs** follow the pattern `^[a-z][a-z0-9_]*$`.
- **`generate_docx(data)`** is the required entry point for all templates. `data` is a dict keyed by field `id`. All values are strings (complex types like address/repeater are JSON strings).
- The HTML app fetches schemas/templates from GitHub via the public API — file paths in schemas (e.g., `"template": "templates/onboarding.py"`) are relative to the repo root.
- Adding a new field type touches these places:
  1. `fieldCreators` map + new `create*Field()` function in index.html
  2. `collectFormData()` in index.html
  3. `populateForm()` in index.html
  4. `validateSection()` in index.html (if the type needs special validation, e.g. address/checkbox/radio)
  5. `_schema.spec.json` — `fieldType` enum + `allOf` exclusion blocks for type-specific properties
  6. Template `.py` files, `docs/FIELD_TYPES.md`, and the expected-types set in `tests/test_schemas.py`

## Development

No build system or package manager. Pyodide and python-docx load from CDN at runtime.

```bash
# Run locally — open index.html directly or use HTTP server for CORS
python -m http.server 8000

# Run all tests (95 tests)
PYTHONPATH=. python -m pytest tests/ -v

# Run a single test file
PYTHONPATH=. python -m pytest tests/test_stencils.py -v

# Run a single test
PYTHONPATH=. python -m pytest tests/test_stencils.py::test_new_doc_creates_document -v

# Lint
ruff check templates/ tests/ --fix
ruff format templates/ tests/
```

### Test structure

- `tests/test_stencils.py` — Unit tests for all `stencils.py` utilities (50 tests)
- `tests/test_templates.py` — Integration tests that load each template with sample data and verify valid DOCX output (10 tests)
- `tests/test_schemas.py` — Schema validation tests: validates all schemas against `_schema.spec.json`, plus negative tests for invalid schemas, wizard, and visible_when (35 tests)
- `tests/fixtures/*.json` — Sample form data matching each schema's field IDs
- Templates are loaded via `importlib.util.spec_from_file_location()` with `sys.path` including `templates/` so `import stencils` resolves

## CI/CD

`.github/workflows/validate.yml` runs on push/PR to `develop` and `main`:
1. Schema validation — validates all `schemas/*.json` against `_schema.spec.json` using `jsonschema`
2. Test execution — runs `PYTHONPATH=. pytest tests/ -v` on Python 3.12

## GitHub Issues

Each issue includes a journaling task to update `docs/DEVLOG.md`.

## Design Context

### Users
Small business operations staff who need to fill out forms and generate professional documents (onboarding packets, expense reports, etc.) without IT overhead. They are non-technical, task-focused, and want to get in and out quickly. FormForge is a tool they reach for when they have a specific job to do — not something they explore for fun.

### Brand Personality
**Clean, precise, confident.** Professional tool feel — minimal decoration, everything intentional. The UI should communicate competence and reliability without being cold or intimidating.

### Emotional Goals
- **Confidence & trust** — Users should feel assured the tool works correctly and their data stays local
- **Ease & calm** — Forms feel effortless, no friction or confusion
- **Speed & efficiency** — Get in, fill the form, get the document

### Aesthetic Direction
- **Dark-mode only** with indigo accent (`#6366f1`) as the primary interactive color
- **Typography:** DM Sans (UI text) + JetBrains Mono (technical labels, badges, status indicators)
- **Spacing:** Consistent 10px radius, generous card padding (28px), 12-16px component gaps
- **Surfaces:** Layered dark backgrounds (`#0f1117` → `#181a22` → `#1f2230`) with subtle 1px borders
- **Interactions:** Smooth 0.2s transitions, subtle hover lifts on cards, indigo focus glow rings
- **Anti-references:** Avoid playful/whimsical aesthetics, excessive color, or busy layouts. This is not a consumer app — it's a focused productivity tool.

### Design Tokens (`:root` in `index.html`)
All design values are centralized as CSS custom properties. When adding or modifying styles, always use tokens rather than hard-coded values.

| Category | Tokens | Notes |
|----------|--------|-------|
| **Colors** | `--bg`, `--surface`, `--surface-2`, `--border`, `--border-focus`, `--text`, `--text-muted`, `--text-on-accent`, `--accent`, `--accent-hover`, `--accent-glow`, `--accent-subtle`, `--accent-border`, `--accent-border-strong`, `--accent-overlay`, `--accent-hover-border`, `--success`, `--success-subtle`, `--warning`, `--error`, `--error-hover`, `--error-glow`, `--error-subtle` | Three-tier surface hierarchy: bg → surface → surface-2. Use `--text-on-accent` for white text on accent/semantic backgrounds. |
| **Fonts** | `--font-sans` (DM Sans), `--font-mono` (JetBrains Mono) | Use `--font-mono` for labels, badges, status, counters. Use `--font-sans` for everything else. |
| **Type scale** | `--text-2xs` (10), `--text-xs` (11), `--text-sm` (12), `--text-sm-md` (13), `--text-base` (14), `--text-md` (15), `--text-lg` (16), `--text-lg-xl` (18), `--text-xl` (20), `--text-2xl` (28), `--text-3xl` (32) | Base is 14px. Mono-label pattern: `var(--text-sm)` + `var(--font-mono)` + `var(--text-muted)` |
| **Radii** | `--radius-xs` (4), `--radius-sm` (6), `--radius-md` (8), `--radius` / `--radius-lg` (10), `--radius-pill` (20) | `--radius-md` (8px) is the default for inputs and buttons. `--radius` (10px) for cards/sections. |
| **Shadows** | `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl` | Used sparingly — only on hover-lifts, dropdowns, toasts, and overlays. |
| **Transitions** | `--transition-fast` (0.15s), `--transition-base` (0.2s), `--transition-slow` (0.3s) | Default to `--transition-base`. Use `--transition-fast` for micro-interactions. |

### Reusable Patterns
- **`.mono-label`** — Utility class for the mono-label pattern (12px JetBrains Mono, muted). Apply via class or replicate the three properties.
- **Card surface** — `background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px` (used by `.config-card`, `.picker-card`, `.form-section`)
- **Button base** — All buttons share: `display: inline-flex; align-items: center; gap: 8px; border-radius: var(--radius-md); font-family: var(--font-sans); cursor: pointer; transition: all var(--transition-base)`

### Design Principles
1. **Clarity over decoration** — Every element should serve a purpose. No ornamental flourishes.
2. **Progressive disclosure** — Show only what's needed at each step. Wizard mode and conditional visibility reflect this at the feature level; design should reinforce it visually.
3. **Quiet confidence** — The UI should feel solid and trustworthy. Subtle transitions, consistent spacing, and restrained color use build that feeling.
4. **Keyboard-friendly, readable** — Ensure all interactive elements are keyboard-navigable. Maintain strong contrast for text readability. No formal WCAG target, but respect the basics.
5. **Zero-friction flow** — Minimize clicks, reduce cognitive load, keep the user moving toward their document.
