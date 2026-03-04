# FormForge — Project Structure & Expansion Guide

## Current Architecture

FormForge is a **client-side-only** application. There is no server — everything runs in the browser via Pyodide (Python compiled to WebAssembly). GitHub acts as the content management system for form schemas and document templates.

```
Browser
├── index.html                 ← single-file app (HTML + CSS + JS)
├── Pyodide (WASM runtime)     ← loaded from CDN at runtime
│   ├── micropip               ← Python package installer
│   └── python-docx            ← installed at runtime via micropip
│
GitHub Repo (your content)
├── schemas/*.json             ← form definitions
└── templates/*.py             ← python-docx generation scripts
```

The data flow is: **GitHub → Browser → Pyodide → DOCX download**. No data ever leaves the user's machine except the initial fetch from GitHub.

---

## Recommended Project Structure

As you add forms, features, and contributors, move from the single HTML file to a proper repo layout:

```
form-forge/
│
├── index.html                     ← entry point (always stays as single file)
│
├── schemas/
│   ├── _schema.spec.json          ← JSON Schema that validates all form schemas
│   ├── onboarding.json
│   ├── expense-report.json
│   ├── incident-report.json
│   └── exit-interview.json
│
├── templates/
│   ├── _base.py                   ← shared helper functions for all templates
│   ├── onboarding.py
│   ├── expense-report.py
│   ├── incident-report.py
│   └── exit-interview.py
│
├── tests/
│   ├── test_schemas.py            ← validate all schemas against spec
│   ├── test_templates.py          ← run each template with sample data
│   └── fixtures/
│       ├── onboarding_sample.json ← sample form data for testing
│       └── expense_sample.json
│
├── docs/
│   ├── SCHEMA_GUIDE.md            ← how to write a new schema
│   ├── TEMPLATE_GUIDE.md          ← how to write a new template
│   └── FIELD_TYPES.md             ← reference for all supported field types
│
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        └── validate.yml           ← CI: lint schemas, run template tests
```

---

## Expansion Areas

### 1. More Field Types

Current types: `text`, `email`, `tel`, `date`, `textarea`, `longtext`, `select`, `radio`, `checkbox`, `list`.

Practical additions and where to implement them:

| New Type | HTML Rendering | Data Format | DOCX Rendering |
|----------|---------------|-------------|----------------|
| `number` | `<input type="number">` with min/max/step | `"42.5"` (string) | Plain text in table |
| `currency` | Number input with currency prefix | `"1250.00"` | Formatted like `$1,250.00` |
| `file` | File upload input | base64 string | Embedded image or attachment note |
| `signature` | Canvas-based signature pad | base64 PNG | `ImageRun` in python-docx |
| `address` | Multi-field group (street, city, state, zip) | JSON string | Formatted multi-line |
| `repeater` | Dynamic group — add N copies of a field set | JSON array string | Repeated table rows |
| `heading` | Non-input — renders as a section divider | (skipped) | (skipped) |
| `hidden` | Not rendered | Static value | Passed to template |

To add a new field type, you touch three places:

1. **`createField()` in the HTML** — add a `case` to the switch statement
2. **`collectFormData()`** — handle any special serialization
3. **Template `.py` file** — parse and render it in the DOCX

The schema JSON doesn't need to change structurally — just use your new type string in `"type"`.

### 2. Shared Template Base (`_base.py`)

Right now each template repeats helper functions. Extract shared utilities:

```python
# templates/_base.py
"""
Shared helpers for all FormForge DOCX templates.
Import this at the top of any template file.
"""

import io
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


def new_doc(title_text, subtitle_text=""):
    """Create a styled Document with a title and optional subtitle."""
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Segoe UI"
    style.font.size = Pt(11)

    title = doc.add_heading(title_text, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x66)

    if subtitle_text:
        doc.add_paragraph("")
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(subtitle_text)
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x99)

    doc.add_paragraph("")
    return doc


def add_table_section(doc, heading, rows):
    """Add a heading + two-column key/value table."""
    # ... (shared implementation)


def add_longtext(doc, heading, text):
    """Add a heading + paragraphs from newline-separated text."""
    # ...


def add_bullet_list(doc, heading, items_str):
    """Add a heading + bullet list from newline-separated string."""
    # ...


def add_signatures(doc, labels):
    """Add a signature block with underlines and labels."""
    # ...


def finalize(doc):
    """Serialize a Document to bytes."""
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
```

**Pyodide caveat:** You can't do a normal `import _base` because Pyodide doesn't have your repo on its filesystem. Two approaches:

- **Approach A (recommended):** Fetch `_base.py` from GitHub and `exec()` it into Pyodide before loading the template. The HTML app would fetch and run it once during init.
- **Approach B:** Inline the base code into each template (use a build script to concatenate).

### 3. Schema Validation & Authoring

Create a JSON Schema spec that validates your form schemas:

```json
// schemas/_schema.spec.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["title", "sections"],
  "properties": {
    "title": { "type": "string" },
    "description": { "type": "string" },
    "icon": { "type": "string", "maxLength": 2 },
    "template": { "type": "string" },
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "fields"],
        "properties": {
          "title": { "type": "string" },
          "fields": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "label", "type"],
              "properties": {
                "id":          { "type": "string", "pattern": "^[a-z][a-z0-9_]*$" },
                "label":       { "type": "string" },
                "type":        { "enum": ["text","email","tel","date","textarea",
                                          "longtext","select","radio","checkbox","list"] },
                "required":    { "type": "boolean" },
                "placeholder": { "type": "string" },
                "hint":        { "type": "string" },
                "options":     { "type": "array", "items": { "type": "string" } },
                "maxLength":   { "type": "integer", "minimum": 1 }
              }
            }
          }
        }
      }
    }
  }
}
```

Use this in CI to catch malformed schemas before they reach users.

### 4. Testing Templates Locally

Each template is a standalone Python script. Test them without a browser:

```python
# tests/test_templates.py
import json
import importlib.util
from pathlib import Path

FIXTURES = Path("tests/fixtures")
TEMPLATES = Path("templates")

def load_template(name):
    spec = importlib.util.spec_from_file_location(name, TEMPLATES / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_onboarding():
    data = json.loads((FIXTURES / "onboarding_sample.json").read_text())
    mod = load_template("onboarding")
    result = mod.generate_docx(data)
    assert isinstance(result, bytes)
    assert len(result) > 0
    # Verify it's a valid ZIP (docx is a ZIP)
    assert result[:2] == b"PK"
```

Run with `pytest tests/` as part of your workflow.

### 5. Multi-Step / Wizard Forms

For long forms, add a `"wizard": true` flag to the schema and split sections into steps:

```json
{
  "title": "Insurance Claim",
  "wizard": true,
  "sections": [
    { "title": "Step 1: Claimant Info", "step": 1, "fields": [...] },
    { "title": "Step 2: Incident Details", "step": 2, "fields": [...] },
    { "title": "Step 3: Review & Submit", "step": 3, "fields": [...] }
  ]
}
```

The HTML builder would detect `wizard: true` and render a step indicator with next/back navigation instead of showing all sections at once.

### 6. Conditional / Dynamic Fields

Add `"visible_when"` to fields so they appear based on other field values:

```json
{
  "id": "other_laptop",
  "label": "Describe your laptop needs",
  "type": "text",
  "visible_when": { "field": "laptop_preference", "equals": "Custom / Other" }
}
```

Implementation is a few lines in the form builder — listen for changes on the referenced field and toggle visibility of the dependent field.

### 7. PDF Export (Alternative to DOCX)

Some users prefer PDF. Pyodide can run `fpdf2`:

```python
# In template .py file, alongside or instead of generate_docx:
from fpdf import FPDF

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text=f"Onboarding: {data['first_name']} {data['last_name']}")
    # ...
    return bytes(pdf.output())
```

Add a schema-level flag: `"export_formats": ["docx", "pdf"]`, and show a format picker in the UI before export.

### 8. CI / GitHub Actions

```yaml
# .github/workflows/validate.yml
name: Validate Schemas & Templates
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install python-docx jsonschema pytest
      - run: python -c "
          import json, jsonschema
          spec = json.load(open('schemas/_schema.spec.json'))
          from pathlib import Path
          for f in Path('schemas').glob('*.json'):
              if f.name.startswith('_'): continue
              schema = json.load(open(f))
              jsonschema.validate(schema, spec)
              print(f'  ✓ {f.name}')
          "
      - run: pytest tests/ -v
```

---

## Roadmap Suggestion

A practical order to build these out, roughly by impact and effort:

| Phase | What | Why |
|-------|------|-----|
| **Now** | Add 2-3 more schemas + templates | Proves the pattern works at scale |
| **Soon** | Shared `_base.py` + auto-fetch in HTML | Eliminates duplication across templates |
| **Soon** | `_schema.spec.json` + CI validation | Catches errors before they reach users |
| **Next** | Conditional fields (`visible_when`) | Huge UX win for complex forms |
| **Next** | `number` and `currency` field types | Most commonly requested missing types |
| **Later** | Wizard mode for multi-step forms | Better UX for 20+ field forms |
| **Later** | PDF export option | Some orgs prefer PDF |
| **Later** | Signature pad field type | Needed for compliance-heavy forms |
| **Someday** | Repeater fields | Complex but powerful (line items, etc.) |

---

## Key Architectural Decisions to Keep in Mind

**Stay client-side.** The biggest strength of this project is that it needs zero infrastructure. No server, no database, no auth (beyond GitHub tokens). Every feature should preserve this property.

**GitHub is your CMS.** Schemas and templates are versioned, reviewable via PRs, and accessible via a stable API. Don't fight this — lean into it. Branch-based staging (`main` vs `draft`) comes free.

**Pyodide is powerful but has limits.** It can run most pure-Python packages, but anything with C extensions that isn't pre-built for Emscripten won't work. `python-docx` and `fpdf2` both work. `openpyxl` works too if you ever want Excel export. Check the [Pyodide packages list](https://pyodide.org/en/stable/usage/packages-in-pyodide.html) before committing to a new library.

**Templates are just Python.** This means anyone comfortable with Python can create new document types without touching the frontend at all. That separation is the core of the design — protect it.
