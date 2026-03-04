# FormForge Development Log

> A running journal of progress, decisions, and notes as the project evolves.

---

## How to Use This Log

- Add entries in reverse-chronological order (newest first)
- Each entry should include: date, related issue(s), what was done, and any decisions or rationale
- Keep entries concise but useful for future reference

---

## Log

### 2026-03-04 — Fix Blank-Canvas Detection for Signature Field (#17)
**Issues:** #17 (Add signature field type)

- Fixed required-field validation for signature fields — `canvas.toDataURL()` always returns a non-empty base64 string even for a blank canvas, so validation was passing without any drawing
- Added `isCanvasBlank()` utility in `index.html` that checks the alpha channel of all pixels to determine if the canvas has actual drawn content
- Updated `endDraw()` to set the hidden input to empty string when canvas is blank, making the existing `validateForm()` logic work correctly for required signatures
- No changes needed to `validateForm()`, `collectFormData()`, schemas, CSS, templates, or tests
- All 46 tests pass with no regressions

**Decisions:**
- Used alpha-channel pixel scanning (`getImageData`) rather than comparing `toDataURL()` against a reference blank — more robust across browsers and canvas sizes
- Set hidden input to empty string (rather than adding special validation logic) so the existing `!val || val.trim() === ''` check in `validateForm()` handles it naturally

---

### 2026-03-03 — Add Demo Schema Exercising All Field Types, Wizard, and Conditionals
**Issues:** #19

- Created `schemas/field-type-demo.json` — "Event Registration" wizard form with 4 steps, all 17 field types, and 3 `visible_when` conditionals
- Created `templates/field-type-demo.py` — template handling all field types including JSON-parsed address, repeater, file, and signature
- Created `tests/fixtures/field-type-demo_sample.json` — comprehensive sample data
- Added 2 template tests (`test_field_type_demo_generates_valid_docx`, `test_field_type_demo_with_empty_data`)
- All 46 tests pass; schema validates against `_schema.spec.json`

**Conditional visibility demonstrated:**
- `venue_address` (address) → shown when `attendance_mode` = "In-person"
- `dietary_restrictions` (checkbox) → shown when `attendance_mode` = "In-person"
- `virtual_platform` (text) → shown when `attendance_mode` = "Virtual"

---

### 2026-03-03 — Filter _schema.spec.json from Schema Picker
**Issues:** #26

- `_schema.spec.json` was appearing in the web UI schema picker and failing to load when selected
- Added `!f.name.startsWith('_')` filter in `index.html` to exclude all `_`-prefixed JSON files from the listing
- Convention: `_`-prefixed files in `schemas/` are internal infrastructure, not form definitions

---

### 2026-03-03 — Updated FIELD_TYPES.md to Reflect Current Project State
**Issues:** documentation maintenance

- Verified all 17 field types in `schemas/_schema.spec.json` `fieldType` enum match what is documented.
- Added `maxLength` to the `text` type section — the spec allows it on both `text` and `longtext`, but the old doc only mentioned it under `longtext`.
- Corrected `longtext` `maxLength` behavior: defaults to `5000` in the counter display, does not hard-truncate, only turns the counter red when exceeded.
- Clarified `currency` behavior: `step="0.01"` and `min="0"` are fixed in the browser regardless of schema; `currency_symbol` defaults to `"$"`.
- Noted that `hidden` restores `default_value` on form reset (handled in `resetForm()` in `index.html`).
- Added explicit note that `min`/`max`/`step` are forbidden on all types except `number`, and `currency_symbol` is forbidden on all types except `currency`, per the schema spec `allOf` constraints.
- Added "Common Optional Properties" table covering `required`, `placeholder`, `hint`, and `visible_when` as cross-cutting concerns.
- Rewrote `list` section to clarify the bulk-paste converts on blur (not on input), and that one empty row is pre-populated on render.
- Updated `address` section to document the actual sub-input IDs (`{id}_street`, `{id}_city`, `{id}_state`, `{id}_zip`) and note the absence of an `id = field.id` element.
- Updated `repeater` section to explicitly list permitted sub-field types (`text`, `email`, `tel`, `number`, `currency`, `select`) sourced from `repeaterFieldType` in the spec; noted `min_rows` behavior (remove button disabled at minimum).
- Added a dedicated "Conditional Visibility (`visible_when`)" section documenting: schema shape, CSS class mechanics, validation skip behavior, supported source types per listener attachment logic in `setupConditionalVisibility()`, and target type limitations (types without a direct `id = field.id` element — `checkbox`, `radio`, `list`, `address`, `repeater`, `heading` — do not work reliably as targets).
- Added note that `heading` cannot be used as a `visible_when` target (no `id = field.id` element rendered).

### 2026-03-03 — Updated TEMPLATE_GUIDE.md to Reflect Current Project State
**Issues:** documentation maintenance

- Rewrote `docs/TEMPLATE_GUIDE.md` to accurately reflect the `_base` module introduced in issue #3 and all field types added in issue #2
- Added a dedicated `_base` Module section documenting all six helpers (`new_doc`, `add_table_section`, `add_longtext`, `add_bullet_list`, `add_signatures`, `finalize`) with signatures, parameter descriptions, and usage examples drawn from the actual source in `templates/_base.py`
- Added the full color palette table (`COLOR_DARK_NAVY`, `COLOR_MEDIUM_BLUE`, `COLOR_SOFT_BLUE`, `COLOR_MUTED`, `COLOR_LIGHT_MUTED`) with hex values and intended usage
- Expanded the data dictionary table to cover all 17 field types including `number`, `currency`, `hidden`, `address`, `file`, `signature`, `repeater`; clarified that `heading` is never present in `data`
- Added a Conditional Fields section explaining that `visible_when`-hidden fields arrive as empty strings and require no special template handling — normal empty-check guards suffice
- Added a Wizard Forms section explaining that wizard mode is UI-only; `generate_docx(data)` receives the same flat dict regardless of whether a schema uses `"wizard": true`
- Added Parsing Complex Field Types section with code snippets for `address` (JSON object parse), `repeater` (JSON array parse and iteration), `file`/`signature` (base64 decode and `doc.add_picture()`), `number`/`currency` (numeric conversion with `try/except`), `checkbox` (split on comma), `longtext`/`list` (split on newline)
- All parse examples include `try/except` guards matching the pattern used in `templates/expense-report.py`
- Updated local testing instructions to reference `PYTHONPATH=. python -m pytest tests/ -v` and the `tests/fixtures/` directory; replaced the outdated one-liner with the `importlib.util.spec_from_file_location()` pattern used by the actual test suite
- Removed the Helper Function Pattern section (superseded by the `_base` module documentation)
- Removed hand-rolled signature block, key-value table, and `add_bullet_list` snippets that duplicated `_base` internals; retained only the Manual key-value table and colored footer examples under Common python-docx Patterns for cases requiring direct `python-docx` control

---

### 2026-03-03 — Updated SCHEMA_GUIDE.md to Reflect Current Project State
**Issues:** documentation maintenance

- Added `wizard` to the top-level structure table with type, required, and description columns
- Added `step` to the sections table (optional integer, minimum 1, defaults to index + 1)
- Expanded the field properties table to cover all spec-enforced properties: `default_value`, `fields`, `maxLength` (text + longtext), `min`/`max`/`step` (number only), `currency_symbol` (currency only), `accept`/`max_size_mb` (file only), `min_rows`/`max_rows` (repeater only), `visible_when`
- Corrected `maxLength` documentation: allowed on both `text` and `longtext` (was listed as `longtext` only in the old field table)
- Added field types table listing all 17 types with their `options` requirement and special properties
- Added "Wizard Mode" section with schema example, explanation of `step` defaulting, per-step validation behavior, and non-wizard backward compatibility note
- Added "Conditional Visibility" section with full `visible_when` schema example, property table, and behavior details (hidden fields skip required validation, always collected as empty string, source can appear anywhere, multiple dependents supported)
- Added "Repeater Sub-Fields" section with sub-field type restriction list and template note
- Added "Validation" section with local validation command
- Updated top-level and section tables to include `Type` column and `additionalProperties: false` note
- Updated field ID documentation with explicit pattern explanation and failure examples (uppercase, hyphen, leading digit)
- Added a note to the file location section that `_schema.spec.json` is excluded from the picker

---

### 2026-03-03 — Updated README.md to Reflect Current Project State
**Issues:** documentation maintenance

- Rewrote `README.md` to accurately reflect all features added in issues #2–#9
- Added wizard mode (`"wizard": true`) section with schema example
- Added conditional field visibility (`visible_when`) section with schema example
- Updated the field type table to cover all 17 supported types (was previously showing only 10)
- Updated project structure tree to include `_schema.spec.json`, `_base.py`, individual test files with counts, and all docs
- Updated "Adding a New Form" template example to use `_base` helpers instead of raw `python-docx`
- Added CI section describing the GitHub Actions workflow (`validate.yml`) and the 44-test count
- Removed outdated manual template testing snippet (still available in `docs/TEMPLATE_GUIDE.md`)

---

### 2026-03-03 — CI with GitHub Actions (#9)
**Issues:** #9 (Set up CI with GitHub Actions)

- Created `.github/workflows/validate.yml` with two jobs: schema validation and pytest
- Triggers on `push` and `pull_request` to `develop` and `main` branches
- Uses `ubuntu-latest`, Python 3.12, installs `python-docx`, `jsonschema`, `pytest`
- Schema validation step validates all `schemas/*.json` (excluding `_schema.spec.json`) against the spec
- Test step runs `PYTHONPATH=. pytest tests/ -v` (44 tests)

**Decisions:**
- Scoped triggers to `develop` and `main` branches only — avoids unnecessary CI runs on ephemeral branches
- Used inline Python for schema validation rather than a separate script — keeps the repo simple and avoids adding a new file for a few lines of code
- Followed the workflow structure from `docs/FORMFORGE_EXPANSION_GUIDE.md` Section 8

---

### 2026-03-03 — Conditional Field Visibility with `visible_when` (#7)
**Issues:** #7 (Add conditional/dynamic field visibility)

- Updated `schemas/_schema.spec.json` to allow optional `visible_when` object on field definitions with required `field` (matching field ID pattern) and `equals` (string) properties, plus `additionalProperties: false`
- Added `setupConditionalVisibility()` in `index.html` — builds a dependency map from source field IDs to dependent fields, attaches `change`/`input` event listeners based on source field type (select/radio use `change`, text/textarea use `input`+`change`), and evaluates initial state
- Added `getFieldValue()` helper that handles radio, checkbox, and standard input/select value retrieval
- Added `isFieldConditionallyHidden()` check used by `validateForm()` and `wizardValidateStep()` to skip validation of hidden conditional fields
- `collectFormData()` unchanged — always collects all fields (hidden ones return empty strings), ensuring templates always receive every key
- `resetForm()` calls `setupConditionalVisibility()` after reset to re-evaluate all conditions
- Added CSS class `conditional-hidden` with `display: none`
- Added 5 new tests to `tests/test_schemas.py`: visible_when validates, missing field rejected, missing equals rejected, extra property rejected, existing schemas regression
- All 44 tests pass

**Decisions:**
- `visible_when` uses simple `equals` string matching — sufficient for the current use case and keeps the schema spec clean. More complex operators (not_equals, contains, etc.) can be added later by extending the `visible_when` object
- Conditional fields are hidden via a CSS class on `.field-group` rather than removing from DOM — preserves form state so Back button in wizard mode doesn't lose data
- `collectFormData()` always includes hidden conditional fields (as empty strings) rather than omitting them — ensures templates always receive a consistent set of keys regardless of visibility state
- Event listeners support order-independent references: a field can depend on a source that appears later in the schema since listeners are attached after all fields are rendered
- Multiple fields can depend on the same source field via the dependency map pattern

---

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
