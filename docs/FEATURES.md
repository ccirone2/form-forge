# FormForge — Feature Inventory & Expansion Guide

> Technical inventory of every entry point, data flow, editing surface, and cross-feature path.
> Use this document when planning new features, auditing coverage, or onboarding contributors.
>
> **Keep this up to date** — when a feature ships, move it from the roadmap into the inventory.

---

## Content Source Entry Points

| # | Entry | How it works |
|---|-------|-------------|
| 1 | **GitHub repo** | Connect → browse schemas → pick form → fill → export DOCX |
| 2 | **Local folder** | FSAA folder picker → discover schemas/templates → same flow |
| 3 | **Drag-drop files** | Drop .json + .py individually (FSAA fallback) |
| 4 | **Demo mode** | Embedded schema+template, zero setup |
| 5 | **URL param** (`?data=URL`) | Pre-fill form data from external JSON URL |

## Data Import/Export Paths

| # | Path | Direction | Format |
|---|------|-----------|--------|
| 1 | **DOCX export** | Out | `.docx` via Pyodide + python-docx |
| 2 | **Form data save** | Out | `.json` file download |
| 3 | **Form data load** | In | `.json` file upload → `populateForm()` |
| 4 | **URL data load** | In | `?data=<url>` → fetch JSON → `populateForm()` |
| 5 | **Clipboard paste** | In | Paste JSON data modal → `populateForm()` (#161) |
| 6 | **Profile save** | Internal | localStorage (multi-profile, named via Autofill) |
| 7 | **Profile apply** | Internal | localStorage → autofill matched fields |
| 8 | **Preset save** | Internal | localStorage per-schema, named field subsets (#162) |
| 9 | **Preset apply** | Internal | localStorage → populate selected fields |
| 10 | **Bundle export** | Out | Copy/download schema + template + sample data as `.formforge.json` (#163) |
| 11 | **Bundle import** | In | Paste/drop package → load into Schema + Template editors (#163) |
| 12 | **Autosave** | Internal | localStorage, 2s debounce, per-schema key |
| 13 | **Autosave restore** | Internal | Prompt on form launch if saved data exists |

## Editing Surfaces

| # | Surface | What you can do |
|---|---------|----------------|
| 1 | **Schema editor** (CodeJar) | Write/edit JSON, live preview, validation badge, context menu with all 24 field snippets |
| 2 | **Template editor** (CodeJar) | Write/edit Python, run preview via Pyodide, context menu with stencils snippets |
| 3 | **Schema preview** | Visual form preview, drag-drop reorder fields/sections, insert fields, wrap in wizard |
| 4 | **Sample data editor** | Edit test data JSON, auto-generate from schema |
| 5 | **GitHub commit/push** | Save edits back to repo with branch management |
| 6 | **Local folder save** | Write edits to filesystem via FSAA |

## Cross-Feature Navigation (Bidirectional Flow)

| From | Action | To |
|------|--------|----|
| Picker card | "Edit Schema" | Schema tab |
| Picker card | "Edit Template" | Template tab |
| Form view | "Edit Schema" | Schema tab |
| Schema preview | "Fill Form" | Forms tab with data |
| Logo click | — | Forms tab |

## LLM-Friendly Patterns

- Copy/paste JSON schemas in/out of editors
- Copy/paste Python templates in/out
- JSON form data export/import (round-trip through LLM)
- Context menus with field snippets reduce need to remember syntax
- Auto-generated sample data means less manual setup

---

## Feature Roadmap

Features below are organized by impact on the core goal: **idea → working document workflow in minimal time**. When a feature ships, move it to the appropriate inventory table above and note the issue/PR.

### Tier 1: High Impact — Accelerate Creation

#### Auto-Generate Template from Schema
When you create or edit a schema, you still have to manually write the Python template from scratch. A "Generate Template" button that reads the current schema and produces a complete, working `generate_docx(data)` function — with all fields handled, stencils helpers called, sections mapped, repeaters parsed — closes the biggest friction gap. Schema creation (with LLM help + snippets) is fast; template authoring is where users stall.

#### DOCX Preview in Form View
The Template tab has DOCX preview (mammoth.js rendering), but the Forms tab does not. Users fill a form and blindly download. A "Preview" button next to "Export DOCX" that renders the document inline — reusing the existing mammoth.js pipeline from `devRunPreview()` — eliminates the export-open-check-fix cycle.

#### Copy-to-Clipboard Buttons for LLM Workflows
To use an LLM to help build/edit schemas or templates, users manually select-all and copy from editors. Bundle export/import (#163) covers the combined copy/paste use case. Remaining opportunities:
- "Copy Schema" / "Copy Template" individual buttons on editor toolbars
- "Copy as LLM Prompt" wrapping content with instructions

#### Schema Scaffolding from Field List
Creating a schema requires knowing JSON structure. A "Quick Start" mode where the user types a simple field list — each line is `field_name: type` (e.g., `employee_name: text`, `department: select[Engineering,Marketing,Sales]`) — and the app generates the full schema JSON. Combined with auto-template generation, this creates a path from idea → workflow in under a minute.

### Tier 2: Medium Impact — Reduce Daily Friction

#### Recent Forms / Quick Launch
Every session starts from scratch — connect, browse, select. A "Recent Forms" section on the Forms tab showing the last 3-5 forms used (title + source) with one-click re-launch. Stored in localStorage with source metadata.

#### Form Data History / Saved Submissions
Autosave only keeps the latest in-progress data. A "Submissions" panel logging each export with timestamp, schema name, and form data JSON. Users can browse past submissions, re-load, or re-export. Addresses "update last month's report" and "copy last week's form" patterns.

#### Bulk/Batch Fill from CSV or JSON Array
No way to generate multiple documents from the same template with different data. A "Batch Export" mode that accepts a CSV or JSON array, runs the template for each row, and downloads a zip of DOCX files. Transforms FormForge from single-document to document generation platform.

#### Schema Composition — Reusable Sections
Common field groups (personal info, address, signatures) are duplicated across schemas. Support a `$ref` or `"include"` directive that pulls in shared section definitions (e.g., `"$ref": "sections/personal_info.json"`), resolved at load time.

### Tier 3: Nice-to-Have — Expand Utility

| Feature | Notes |
|---------|-------|
| **Export format options** (PDF, Markdown, text) | PDF via browser print-to-PDF of mammoth.js preview; Markdown/text as form data serialization |
| **Form sharing via URL** | Encode schema pointer in URL: `?repo=owner/repo&schema=path` or `?schema=<base64>` |
| **Conditional visibility enhancements** | Extend `visible_when` with `not_equals`, `in: [values]`, `and`/`or` compound conditions |
| **Form completion progress indicator** | Progress bar showing required fields filled vs. total; per-step completion in wizard mode |
| **Template diff / version compare** | Diff view: current editor vs. saved/committed version using a lightweight diff library |
| **Offline / PWA support** | Service worker caching Pyodide, python-docx, and CDN deps; local folder source already works offline |
| **Import schema from existing DOCX** | Upload DOCX → extract structure hints (headings → sections, fields → types) → generate draft schema |

---

## Priority Summary

| # | Feature | Impact | Effort | Unlocks |
|---|---------|--------|--------|---------|
| 1 | Auto-generate template from schema | Very High | Medium | Idea → working workflow in minutes |
| 2 | DOCX preview in form view | High | Low | Eliminates export-check-fix cycle |
| 3 | Clipboard buttons for LLM workflows | High | Low | Faster LLM-assisted creation |
| 4 | Schema scaffolding from field list | High | Medium | Non-technical users can create forms |
| 5 | Recent forms / quick launch | Medium | Low | Daily use friction reduction |
| 6 | Form data history | Medium | Medium | Re-use and version past submissions |
| 7 | Batch fill from CSV | Medium | Medium | Multi-document generation |
| 8 | Reusable schema sections | Medium | High | Scalable form library |

Features 1–3 together create a dramatically faster creation loop:
**Scaffold fields** → **auto-generate template** → **preview inline** → **copy & refine with LLM** → done.
