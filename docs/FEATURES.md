# FormForge — Feature Inventory & Expansion Guide

> Technical inventory of every entry point, data flow, editing surface, and cross-feature path.
> Use this document when planning new features, auditing coverage, or onboarding contributors.
>
> **Keep this up to date** — when a feature ships, move it from the roadmap into the inventory.

---

## Content Source Entry Points

| # | Entry | How it works |
|---|-------|-------------|
| 1 | **GitHub repo** | Connect dialog (GitHub tab) → enter `owner/repo` + optional branch/token → browse schemas → pick form → fill → export DOCX |
| 2 | **Local folder** | Connect dialog (Local Folder tab) → FSAA folder picker → discover `schemas/*.json` and `templates/*.py` → same flow |
| 3 | **Individual files** | Connect dialog → Local Folder tab → "Or load individual files" expandable → drop/click `.json` + `.py` (FSAA fallback) |
| 4 | **Demo mode** | "Try the demo form" button on Forms tab hero → embedded schema + template, zero setup |
| 5 | **URL param** (`?data=URL`) | Pre-fill form data from external JSON URL via `populateForm()` |

## Data Import/Export Paths

| # | Path | Direction | Format |
|---|------|-----------|--------|
| 1 | **DOCX export** | Out | `.docx` via Pyodide + python-docx (`handleExport()`) |
| 2 | **Form data save** | Out | `.json` file download (Save Data button in submit area, also Ctrl+S) |
| 3 | **Form data load** | In | `.json` file upload via Autofill dropdown → "Load from File" → `populateForm()` |
| 4 | **URL data load** | In | `?data=<url>` → fetch JSON → `populateForm()` (consumed after form launch via `pendingDataUrl`) |
| 5 | **Clipboard paste** | In | Autofill dropdown → "Paste Data" → JSON modal with live validation → `populateForm()` |
| 6 | **Autofill dropdown** | UI | Unified `[Autofill ▾]` button with sections: Profiles, Presets, and actions (Load Sample Data, Paste Data, Load from File). Badge shows count of saved profiles + presets. |
| 7 | **Profile save/apply** | Internal | localStorage (multi-profile, named). Create/edit/delete profiles via Autofill dropdown. Field-level profile dropdown also available on individual fields. |
| 8 | **Preset save/apply** | Internal | localStorage per-schema, named field subsets. Create/edit/delete via Autofill dropdown. |
| 9 | **Bundle export** | Out | Copy to clipboard (with toast + download fallback) or download schema + template + sample data as `.formforge.json`. Available from Schema and Template editor toolbars. |
| 10 | **Bundle import** | In | Paste text or drop `.formforge.json` file via modal → auto-detects bundle, schema JSON, Python template, or form data → loads into Schema + Template editors |
| 11 | **Autosave** | Internal | localStorage, 2s debounce (`AUTOSAVE_DEBOUNCE_MS`), per-schema key. Skips values over 50 KB (`AUTOSAVE_SIZE_LIMIT`). |
| 12 | **Autosave restore** | Internal | Prompt on form launch if saved data exists (restore or discard) |
| 13 | **Copy AI Context** | Out | "Copy AI Context" buttons on Schema and Template editor toolbars — copies LLM-optimized context (schema/template + instructions) to clipboard via `copySchemaAIContext()` / `copyTemplateAIContext()` |

## Editing Surfaces

| # | Surface | What you can do |
|---|---------|----------------|
| 1 | **Schema editor** (CodeJar + Prism.js) | Write/edit JSON with syntax highlighting, 300ms debounce live form preview, real-time validation badge, context-aware right-click menu (field type snippets for all 24 types, Add Section, Wrap in Wizard, Base Scaffold) |
| 2 | **Template editor** (CodeJar + Prism.js) | Write/edit Python with syntax highlighting, run DOCX preview via Pyodide + mammoth.js + DOMPurify, auto-preview on changes, context-aware right-click menu with stencils helper snippets, validation badge |
| 3 | **Schema preview** | Visual live form preview, drag-drop reorder fields and sections, insert fields via right-click context menu, add sections via `+` buttons between sections, "Fill Form" button to test in Forms tab |
| 4 | **Sample data editor** (CodeJar) | Collapsible panel in Template tab, edit test data JSON, auto-generate from schema via "Auto-fill" button (`devAutoFillSampleData()`) |
| 5 | **GitHub commit/push** | Save edits back to repo, create new branches, switch branches. Commit & Push buttons in Schema and Template editor toolbars (visible when connected to GitHub). |
| 6 | **Local folder save** | Write edits to filesystem via FSAA with 5s file polling for external changes (`devWorkspacePoller`) |
| 7 | **Help sidebar** | Contextual reference panels for Schema and Template editors, searchable/filterable, toggled via toolbar button or Ctrl+Shift+H |

## UI Structure

| Component | Description |
|-----------|-------------|
| **Header** | Sticky top bar with FormForge logo (click to go to Forms tab), status badge (mobile only) |
| **Sidebar** | Left navigation with 4 tabs (Forms, Schema, Template, Docs), collapsible via toggle button, connection status badge at bottom that opens Connect dialog |
| **Mobile bottom nav** | Bottom navigation bar (visible at <=768px) mirroring sidebar tabs |
| **Connect dialog** | Modal overlay with two tabs: GitHub and Local Folder. Shows current connection status and disconnect button when connected. |
| **Form view** | Full form with nav bar (Back, source info, autosave indicator, Edit Schema, Autofill), form sections, submit area (Export DOCX, Save Data, Reset), activity log panel |
| **Schema tab** | Split pane: left = JSON editor with toolbar, right = live form preview. Help sidebar available. |
| **Template tab** | Split pane: left = Python editor with toolbar + collapsible sample data panel, right = DOCX preview (mammoth.js rendered). Help sidebar available. |
| **Docs tab** | Embedded documentation with sub-tabs: Schema Guide, Template Guide, Field Types, Examples. Each has Copy and Download .md buttons. Content is built-in (independent of connected source). |

## Cross-Feature Navigation (Bidirectional Flow)

| From | Action | To |
|------|--------|----|
| Picker card | "Schema" button | Schema tab (`loadSchemaIntoEditor()`) |
| Picker card | "Template" button | Template tab (`loadTemplateIntoEditor()`) |
| Picker card | "Open Form" / double-click | Form view (`launchForm()`) |
| Form view | "Edit Schema" button | Schema tab (`editCurrentSchema()`) |
| Form view | Autofill button | Dropdown: Profiles / Presets / Load Sample Data / Paste Data / Load from File |
| Schema preview | "Fill Form" button | Form view (`fillFormFromEditor()`) |
| Logo click | — | Forms tab |
| Sidebar status badge | Click | Connect dialog |

## Form Behavior

| Feature | Description |
|---------|-------------|
| **24 field types** | text, email, tel, date, textarea, longtext, select, radio, checkbox, list, number, currency, heading, hidden, info, address, file, signature, repeater, time, url, toggle, datetime, multi_select |
| **Wizard mode** | Schemas with `"wizard": true` render as multi-step forms with numbered step indicator (circles + connectors), Next/Back navigation, and per-step validation. Submit only available on final step. Data preserved across step navigation. Wizard steps are drag-reorderable in schema preview. |
| **Conditional visibility** | Fields with `visible_when: { field, equals }` are shown/hidden based on another field's value. Hidden fields are skipped by required validation but still collected as empty strings in `collectFormData()`. |
| **Inline sample data** | Schemas can include `sampleData` object for one-click form population via "Load Sample Data" in Autofill dropdown. Falls back to fixture files in `tests/fixtures/`. |
| **Form validation** | Per-section validation with inline error messages. Required fields, type-specific validation (email, address, checkbox, radio). |
| **Reset form** | Reset button clears all form fields. |
| **Dirty guard** | Warns before leaving form view if data exists (Escape key or browser unload). |

## Keyboard Shortcuts

| Shortcut | Context | Action |
|----------|---------|--------|
| **Ctrl+S** | Form view | Save form data as JSON |
| **Ctrl+S** | Schema/Template tab | Save editor content (to filesystem or memory) |
| **Ctrl+Enter** | Form view | Export to DOCX |
| **Ctrl+Enter** / **Shift+Enter** | Template tab | Run DOCX preview |
| **Ctrl+Shift+H** | Schema/Template tab | Toggle help sidebar |
| **Escape** | Form view | Dismiss dropdowns, then back to picker (with dirty guard) |
| **Escape** | Modals/Dropdowns | Close current modal or dropdown |

## LLM-Friendly Patterns

- Copy/paste JSON schemas in/out of editors
- Copy/paste Python templates in/out
- **Copy AI Context** buttons on Schema and Template toolbars — copies LLM-optimized context with instructions
- JSON form data export/import (round-trip through LLM)
- Paste JSON data via clipboard modal (Autofill → Paste Data)
- Bundle export/import for schema + template + data as one `.formforge.json` artifact
- Profile/preset reuse for boilerplate data
- Context menus with field snippets reduce need to remember syntax
- Auto-generated sample data means less manual setup
- Base Scaffold via context menu for quick schema bootstrapping

## CDN Dependencies

All loaded at runtime from jsDelivr (no build step):

| Library | Version | Purpose |
|---------|---------|---------|
| Pyodide | 0.24.1 | Python-in-WebAssembly runtime for DOCX generation |
| Prism.js | 1.29.0 | Syntax highlighting (JSON + Python) in editors |
| CodeJar | 4.2.0 | Lightweight code editor |
| mammoth.js | 1.6.0 | DOCX-to-HTML conversion for preview |
| DOMPurify | 3.2.4 | HTML sanitization for mammoth output |
| python-docx | (via micropip) | DOCX document creation in Pyodide |

Prism CSS is preloaded. All JS libraries are lazy-loaded on first Schema/Template tab click (via `loadDevDeps()`), except Pyodide which loads on first form launch or export.

---

## Feature Roadmap

Features below are organized by impact on the core goal: **idea → working document workflow in minimal time**. When a feature ships, move it to the appropriate inventory table above and note the issue/PR.

### Tier 1: High Impact — Accelerate Creation

#### Auto-Generate Template from Schema
When you create or edit a schema, you still have to manually write the Python template from scratch. A "Generate Template" button that reads the current schema and produces a complete, working `generate_docx(data)` function — with all fields handled, stencils helpers called, sections mapped, repeaters parsed — closes the biggest friction gap. Schema creation (with LLM help + snippets) is fast; template authoring is where users stall.

#### DOCX Preview in Form View
The Template tab has DOCX preview (mammoth.js rendering), but the Forms tab does not. Users fill a form and blindly download. A "Preview" button next to "Export DOCX" that renders the document inline — reusing the existing mammoth.js pipeline from `devRunPreview()` — eliminates the export-open-check-fix cycle.

#### Schema Scaffolding from Field List
Creating a schema requires knowing JSON structure. A "Quick Start" mode where the user types a simple field list — each line is `field_name: type` (e.g., `employee_name: text`, `department: select[Engineering,Marketing,Sales]`) — and the app generates the full schema JSON. Combined with auto-template generation, this creates a path from idea → workflow in under a minute. **Note:** A basic `BASE_SCAFFOLD` context menu option already exists for bootstrapping an empty schema with one section and field; this roadmap item covers the more advanced field-list parsing approach.

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
| 3 | Schema scaffolding from field list | High | Medium | Non-technical users can create forms |
| 4 | Recent forms / quick launch | Medium | Low | Daily use friction reduction |
| 5 | Form data history | Medium | Medium | Re-use and version past submissions |
| 6 | Batch fill from CSV | Medium | Medium | Multi-document generation |
| 7 | Reusable schema sections | Medium | High | Scalable form library |

Features 1-2 together create a dramatically faster creation loop:
**Scaffold fields** → **auto-generate template** → **preview inline** → **copy & refine with LLM** → done.
