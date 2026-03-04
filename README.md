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
│   └── *.json                  ← form definitions
├── templates/
│   ├── _base.py                ← shared helpers for all templates
│   └── *.py                    ← Python DOCX generation scripts
├── tests/
│   ├── fixtures/               ← sample data for template tests
│   ├── test_base.py            ← unit tests for _base.py utilities (14 tests)
│   ├── test_templates.py       ← integration tests for templates (4 tests)
│   └── test_schemas.py         ← schema validation tests (26 tests)
├── docs/
│   ├── DEVLOG.md               ← development journal
│   ├── SCHEMA_GUIDE.md         ← guide for writing new schemas
│   ├── TEMPLATE_GUIDE.md       ← guide for writing new templates
│   └── FIELD_TYPES.md          ← reference for all 17 field types
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

Every template must export a `generate_docx(data)` function that accepts a dict (keyed by field `id`) and returns DOCX bytes. Use the shared `_base` helpers:

```python
import _base

def generate_docx(data):
    doc = _base.new_doc("My Document")
    doc.add_paragraph(f"Name: {data.get('field_name', '')}")
    return _base.finalize(doc)
```

See `docs/TEMPLATE_GUIDE.md` for the full `_base` API.

## Supported Field Types

| Type | Renders As | Data Format |
|------|-----------|-------------|
| `text` | Single-line input | `str` |
| `email` | Email input | `str` |
| `tel` | Phone input | `str` |
| `date` | Date picker | `str` (`YYYY-MM-DD`) |
| `textarea` | Multi-line text | `str` |
| `longtext` | Large textarea with character counter | `str` (may contain `\n`) |
| `select` | Dropdown | `str` |
| `radio` | Radio buttons | `str` |
| `checkbox` | Checkboxes | `str` (comma-separated) |
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

- **Schema validation** — validates all `schemas/*.json` against `schemas/_schema.spec.json`
- **Tests** — runs `PYTHONPATH=. pytest tests/ -v` (44 tests)

See `.github/workflows/validate.yml`.

## Development

```bash
# Run locally
python -m http.server 8000

# Run all tests (44 tests)
PYTHONPATH=. python -m pytest tests/ -v

# Lint
ruff check templates/ tests/ --fix
ruff format templates/ tests/
```

## License

[MIT](LICENSE)
