# FormForge Development Log

> A running journal of progress, decisions, and notes as the project evolves.

---

## How to Use This Log

- Add entries in reverse-chronological order (newest first)
- Each entry should include: date, related issue(s), what was done, and any decisions or rationale
- Keep entries concise but useful for future reference

---

## Log

### 2026-03-03 — Multi-Step Wizard Form Support (#6)
**Issues:** #6 (Add multi-step wizard form support)

- Updated `schemas/_schema.spec.json` to allow optional `"wizard": true` boolean at the top level and optional `"step"` (positive integer, minimum 1) on section objects
- Added wizard CSS styles to `index.html`: step indicator with circles, connectors, and labels; navigation buttons; section visibility toggling
- Modified `buildForm()` in `index.html` to detect `wizard: true` and render a step indicator, show only one section at a time, and add Next/Back navigation buttons per section
- Added `wizardValidateStep()` for per-step validation — clicking Next validates only the current section's required fields before advancing
- Added `wizardNext()` and `wizardGoTo()` for step navigation with indicator state updates (active/completed styling)
- Back button hidden on first step; submit area hidden until last step; data preserved across step navigation
- Non-wizard schemas render exactly as before — no visual or behavioral changes
- Added 6 new tests to `tests/test_schemas.py`: wizard schema validation, wizard without step, non-wizard regression, rejects non-boolean wizard, rejects non-integer step, rejects step zero
- All 39 tests pass

**Decisions:**
- Wizard navigation buttons are placed inside each section div rather than in a fixed footer — keeps the flow natural and avoids layout conflicts with the existing submit area
- Submit area (`Export to DOCX` + `Reset`) is hidden during wizard navigation and only shown on the final step, where it replaces the Next button
- Per-step validation reuses the same pattern as `validateForm()` but scoped to one section — `collectFormData()` and full `validateForm()` still operate across all sections for final export
- Step indicator uses numbered circles with connectors — completed steps get accent-glow background, active step gets solid accent fill
- If sections omit `step`, the indicator defaults to section index + 1

---

### 2026-03-03 — Template Testing with pytest (#5)
**Issues:** #5 (Set up template testing with pytest)

- All test infrastructure was created during issues #3 and #4:
  - `tests/test_schemas.py` (15 tests): validates all schemas against `_schema.spec.json`, plus 9 negative tests for invalid schemas
  - `tests/test_templates.py` (4 tests): runs `generate_docx()` for onboarding and expense-report with sample and empty data, verifies valid DOCX output (bytes, non-empty, PK magic bytes)
  - `tests/test_base.py` (14 tests): unit tests for all `_base.py` utilities
  - `tests/fixtures/onboarding_sample.json` and `expense-report_sample.json` with field IDs matching their schemas
- Templates loaded via `importlib.util.spec_from_file_location()` with `sys.path` including `templates/` so `import _base` resolves
- All 33 tests pass with `PYTHONPATH=. python -m pytest tests/ -v`
- No external services or network access required — fully offline

**Decisions:**
- Issue #5 was fully satisfied by work in #3 and #4 — no additional code needed, just verified and closed

---

### 2026-03-03 — Added Schema Validation with `_schema.spec.json` (#4)
**Issues:** #4 (Add schema validation)

- Created `schemas/_schema.spec.json` using JSON Schema draft 2020-12 to validate all form schemas
- Spec validates top-level structure (`title`, `sections`), section structure (`title`, `fields`), and field structure (`id` pattern, `label`, `type` enum)
- All 17 field types enumerated in the `type` enum with type-specific conditional validation via `if/then/allOf`
- Conditional rules enforce: `options` required for select/radio/checkbox, `default_value` for hidden, `fields` for repeater
- Type-specific properties restricted to their correct types (e.g., `min/max/step` only on `number`, `maxLength` only on `text/longtext`, `accept/max_size_mb` only on `file`)
- Repeater sub-fields validated separately with restricted type enum (`text`, `email`, `tel`, `number`, `currency`, `select`)
- Created `tests/test_schemas.py` with 15 tests: spec validity, field type coverage, positive validation of both existing schemas, and 9 negative tests for invalid schemas
- Both `onboarding.json` and `expense-report.json` validate successfully against the spec

**Decisions:**
- Used `if/then` within `allOf` for conditional validation rather than `oneOf` with separate schemas per type — keeps the spec more readable and maintainable
- Used `additionalProperties: false` at all levels to catch typos and unknown properties early
- Template path pattern enforced as `^templates/.+\.py$` to match the project convention
- Repeater sub-fields defined as a separate `$defs/repeaterField` schema with its own restricted type enum, matching the subset supported by the app

---

### 2026-03-03 — Created Shared Template Base `_base.py` (#3)
**Issues:** #3 (Create shared template base)

- Created `templates/_base.py` with 6 shared utilities: `new_doc()`, `add_table_section()`, `add_longtext()`, `add_bullet_list()`, `add_signatures()`, `finalize()`
- Exported a standard color palette (`COLOR_DARK_NAVY`, `COLOR_MEDIUM_BLUE`, `COLOR_SOFT_BLUE`, `COLOR_MUTED`, `COLOR_LIGHT_MUTED`)
- Refactored `templates/onboarding.py` to use `_base` helpers — removed ~90 lines of duplicated helper functions
- Refactored `templates/expense-report.py` to use `_base` helpers for shared patterns (table sections, colors, finalize)
- Updated `index.html` with `loadBaseModule()` function that fetches `_base.py` and writes it to Pyodide's virtual filesystem via `pyodide.FS.writeFile()`, enabling standard `import _base` in templates
- `loadBaseModule()` is called once before any template execution; `baseModuleLoaded` flag prevents re-fetching
- Added `baseModuleLoaded` reset on repo change so new repos get their own `_base.py`
- Created `tests/test_base.py` (14 tests) covering all 6 utilities, color constants, and edge cases
- Created `tests/test_templates.py` (4 tests) verifying both templates produce valid DOCX with sample and empty data
- Created `tests/fixtures/onboarding_sample.json` sample fixture

**Decisions:**
- Used Pyodide's `FS.writeFile()` to place `_base.py` on the virtual filesystem rather than `exec()` into globals — this allows templates to use standard `import _base` syntax that works identically in regular Python and Pyodide
- Kept `Calibri` as the default font (matching existing templates) rather than `Segoe UI` from the expansion guide sketch
- Added optional `font_name` and `font_size` parameters to `new_doc()` for template customization while maintaining backward compatibility
- `loadBaseModule()` tries the connected GitHub repo first, falls back to the FormForge repo on GitHub — works for both custom repos and the demo/local file paths
- Expense report template retains its own signature handling (base64 image embedding) rather than using `add_signatures()` since it needs specialized canvas-to-image logic

---

### 2026-03-03 — Implemented All 8 New Field Types (#2)
**Issues:** #2, #11 (number), #12 (currency), #13 (heading), #14 (hidden), #15 (address), #16 (file), #17 (signature), #18 (repeater), #19 (demo schema)

- Added 8 new field types to `createField()`, `collectFormData()`, `validateForm()`, and `resetForm()` in `index.html`
- Added CSS styles for all new field types (currency wrapper, heading divider, address group, file upload with preview, signature canvas pad, repeater rows)
- Updated `buildForm()` layout: `number` and `currency` pair in 2-column rows; `hidden` skipped from visible layout
- Created `schemas/expense-report.json` — demo form exercising all 8 new types plus existing types
- Created `templates/expense-report.py` — handles JSON parsing for address/repeater, base64 decoding for file/signature, currency formatting
- Created `tests/fixtures/expense-report_sample.json` — sample data for template testing
- Updated `docs/FIELD_TYPES.md` with all 8 new types: JSON schema examples, schema properties, and template handling code

**Decisions:**
- Heading fields return early from `createField()` to skip the default hint rendering (they handle their own hint)
- Hidden fields use `default_value` schema property; the field group is `display: none`
- Address data is serialized as a JSON object string; validation checks street is non-empty when required
- Signature uses `canvas.toDataURL('image/png')` saved to a hidden input on each `mouseup`/`touchend`
- Repeater stores sub-field config via `wrapper.dataset.subFields` for `collectFormData()` to reference
- Repeater sub-fields support text, email, tel, number, currency, and select types
- File upload validates size client-side via `max_size_mb` and shows image preview for image types

---

### 2026-03-03 — Implementation Plan for #2 (New Field Types)
**Issues:** #2, #11–#19

- Analyzed existing codebase: `createField()` (L1393–1541), `collectFormData()` (L1604–1624), form layout (L1341–1391)
- Broke #2 into 9 sub-issues organized by complexity tier:
  - **Tier 1 (simple):** #11 number, #12 currency, #13 heading, #14 hidden
  - **Tier 2 (complex):** #15 address, #16 file, #17 signature, #18 repeater
  - **Integration:** #19 demo schema exercising all new types
- Each issue includes: schema properties, implementation touchpoints, CSS needs, template handling, and acceptance criteria

**Decisions:**
- Implementation order follows the priority in issue #2: number/currency first, heading/hidden next, then complex types
- Repeater depends on Tier 1 types being complete (sub-fields may use number, currency, etc.)
- Data formats: address → JSON object string, repeater → JSON array string, signature/file → base64 string
- Hidden fields use `default_value` schema property (not `value`, to avoid confusion with HTML attribute)
- Heading fields skip `collectFormData()` and `validateForm()` entirely
- Currency defaults to `$` symbol with `step="0.01"`

---

### 2026-03-03 — Project Initialization Complete
**Issues:** #1 (Project Initialization)

- Added `README.md` with project overview, architecture, field types, usage instructions, and how to add forms
- Added `LICENSE` (MIT)
- Created `tests/` and `tests/fixtures/` directories
- Created `.github/workflows/` directory (ready for CI in issue #9)
- Added `.gitignore` for Python, Node, OS, and IDE files
- Verified `schemas/` and `templates/` directories already in place

**Decisions:**
- Chose MIT license for maximum permissiveness
- Used `.gitkeep` files to track empty directories in git

---

### 2026-03-03 — Project Setup
**Issues:** #1 (Project Initialization)

- Created GitHub repo `ccirone2/form-forge` with default branch `develop`
- Added initial `schemas/` and `templates/` directories
- Added `docs/FORMFORGE_EXPANSION_GUIDE.md` as the project roadmap
- Created GitHub issues #1–#9 covering all expansion areas from the guide
- Created this DEVLOG to track progress going forward

**Decisions:**
- Using `develop` as the default branch; `main` reserved for stable releases
- Staying client-side only — no server, no database, no auth (beyond GitHub)
- GitHub serves as the CMS for schemas and templates
