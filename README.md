# FormForge

A **client-side-only** browser application that turns GitHub-hosted JSON schemas into dynamic HTML forms and exports filled data as DOCX documents via [Pyodide](https://pyodide.org/) (Python in WebAssembly).

No server, no database — GitHub is the CMS.

## How It Works

```
GitHub repo → fetch schema JSON + template .py → render form in browser
→ user fills form → Pyodide runs template → DOCX downloads locally
```

1. **Define** a form schema in JSON (`schemas/*.json`)
2. **Write** a Python template that generates a DOCX (`templates/*.py`)
3. **Open** `index.html` — it fetches schemas from GitHub and renders the form
4. **Fill** the form and click Export — Pyodide runs the template in-browser
5. **Download** the generated DOCX — no data ever leaves your machine

## Project Structure

```
form-forge/
├── index.html                  ← single-file app (HTML + CSS + JS)
├── schemas/
│   ├── _schema.spec.json       ← JSON Schema spec that validates all schemas
│   ├── onboarding.json         ← employee onboarding form
│   ├── expense-report.json     ← expense report form
│   └── field-type-demo.json    ← demo form showcasing all field types
├── templates/
│   ├── stencils.py             ← shared helpers for all templates
│   ├── onboarding.py           ← employee onboarding template
│   ├── expense-report.py       ← expense report template
│   └── field-type-demo.py      ← demo template showcasing all field types
├── tests/
│   ├── fixtures/               ← sample data for template tests
│   ├── test_stencils.py        ← unit tests for stencils.py utilities (50 tests)
│   ├── test_templates.py       ← integration tests for templates (10 tests)
│   ├── test_schemas.py         ← schema validation tests (44 tests)
│   └── test_dev_mode.py        ← UI structure and feature tests (320 tests)
├── docs/
│   ├── DEVLOG.md               ← development journal
│   ├── PLAN.md                 ← structured implementation plans
│   ├── SCHEMA_GUIDE.md         ← guide for writing new schemas
│   ├── TEMPLATE_GUIDE.md       ← guide for writing new templates
│   └── FIELD_TYPES.md          ← reference for all 23 field types
└── .github/workflows/
    └── validate.yml            ← CI: schema validation + pytest
```

## Running Locally

No build system or package manager required.

1. Clone the repo
2. Open `index.html` in a browser (or use a local HTTP server for CORS)
3. Pyodide loads automatically from CDN

## Adding a New Form

### 1. Create a schema (`schemas/my-form.json`)

```json
{
  "title": "My Form",
  "description": "A description shown to users",
  "icon": "📝",
  "template": "templates/my-form.py",
  "sections": [
    {
      "title": "Section Name",
      "fields": [
        {
          "id": "field_name",
          "label": "Field Label",
          "type": "text",
          "required": true
        }
      ]
    }
  ]
}
```

### 2. Create a template (`templates/my-form.py`)

Every template must export a `generate_docx(data)` function that accepts a dict (keyed by field `id`) and returns DOCX bytes. Use the shared `stencils` helpers:

```python
import stencils

def generate_docx(data):
    doc = stencils.new_doc("My Document")
    doc.add_paragraph(f"Name: {data.get('field_name', '')}")
    return stencils.finalize(doc)
```

See `docs/TEMPLATE_GUIDE.md` for the full `stencils` API.

## Supported Field Types

| Type | Renders As | Data Format |
|------|-----------|-------------|
| `text` | Single-line input | `str` |
| `email` | Email input | `str` |
| `tel` | Phone input | `str` |
| `date` | Date picker | `str` (`YYYY-MM-DD`) |
| `time` | Time picker | `str` (`HH:MM`) |
| `url` | URL input | `str` |
| `datetime` | Combined date and time picker | `str` (`YYYY-MM-DDTHH:MM`) |
| `textarea` | Multi-line text | `str` |
| `longtext` | Large textarea with character counter | `str` (may contain `\n`) |
| `select` | Dropdown | `str` |
| `radio` | Radio buttons | `str` |
| `checkbox` | Checkboxes | `str` (comma-separated) |
| `multi_select` | Searchable multi-select with tags | `str` (comma-separated) |
| `toggle` | Boolean yes/no switch | `str` (`true`/`false`) |
| `list` | Dynamic add/remove rows | `str` (newline-separated) |
| `number` | Number input with min/max/step | `str` |
| `currency` | Number input with currency prefix | `str` |
| `heading` | Visual section divider | *(not collected)* |
| `hidden` | Passes a static value | `str` |
| `address` | Street/city/state/zip group | JSON string |
| `file` | File upload with image preview | base64 data URI |
| `signature` | Canvas drawing pad | base64 PNG data URI |
| `repeater` | Dynamic rows of sub-fields | JSON array string |

See `docs/FIELD_TYPES.md` for full details on each type, including schema properties and template handling.

## Built-in Tools

FormForge includes always-available tabs for creating and editing forms alongside the form-filling experience. No mode toggle — all tools are accessible from the tab navigation bar.

```
[FormForge]  [Forms] [Schema] [Template] [Docs]     [source badge]
```

- **Forms** — Connect a content source (GitHub repo or local folder), browse available forms, fill them, and export DOCX
- **Schema** — JSON editor with syntax highlighting, live form preview, real-time validation, and right-click context menu with field type snippets
- **Template** — Python editor with DOCX preview powered by Pyodide + mammoth.js, and stencils helper snippets
- **Docs** — Embedded documentation for Schema Guide, Template Guide, Field Types, and example schema/template

Picker cards include "Edit Schema" and "Edit Template" actions for seamless navigation between filling and editing. Editor dependencies (Prism.js, CodeJar, mammoth.js, DOMPurify) are lazy-loaded from CDN on first Schema/Template tab click.

## Schema Features

### Wizard Mode (multi-step forms)

Set `"wizard": true` at the schema top level to render the form as a step-by-step wizard. Each section becomes a step with Next/Back navigation. Required field validation runs per-step before advancing.

```json
{
  "title": "Multi-Step Form",
  "wizard": true,
  "sections": [
    { "title": "Step 1", "step": 1, "fields": [...] },
    { "title": "Step 2", "step": 2, "fields": [...] }
  ]
}
```

### Conditional Field Visibility

Use `visible_when` on any field to hide or show it based on another field's value. The field is hidden until the source field matches the specified value.

```json
{
  "id": "other_reason",
  "label": "Please specify",
  "type": "text",
  "visible_when": { "field": "reason", "equals": "Other" }
}
```

Hidden fields are excluded from validation but are always included in `data` passed to templates (as empty strings).

## CI

GitHub Actions runs on every push and pull request to `develop` and `main`:

- **Lint** — runs `ruff check templates/ tests/`
- **Tests** — runs `PYTHONPATH=. pytest tests/ -v` (436 tests)

See `.github/workflows/validate.yml`.

## Development

```bash
# Run locally
python -m http.server 8000

# Run all tests (436 tests)
PYTHONPATH=. python -m pytest tests/ -v

# Lint
ruff check templates/ tests/ --fix
ruff format templates/ tests/
```

## License

[MIT](LICENSE)
