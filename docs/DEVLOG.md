# FormForge Development Log

> A running journal of progress, decisions, and notes as the project evolves.

---

## How to Use This Log

- Add entries in reverse-chronological order (newest first)
- Each entry should include: date, related issue(s), what was done, and any decisions or rationale
- Keep entries concise but useful for future reference

---

## Log

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
