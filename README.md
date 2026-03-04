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
│   └── *.json                  ← form definitions
├── templates/
│   └── *.py                    ← Python DOCX generation scripts
├── tests/
│   └── fixtures/               ← sample data for template tests
├── docs/
│   ├── DEVLOG.md               ← development journal
│   └── FORMFORGE_EXPANSION_GUIDE.md  ← project roadmap
└── .github/workflows/          ← CI configuration
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

Every template must export a `generate_docx(data)` function that accepts a dict (keyed by field `id`) and returns DOCX bytes:

```python
import io
from docx import Document

def generate_docx(data):
    doc = Document()
    doc.add_heading("My Document", level=0)
    doc.add_paragraph(f"Name: {data.get('field_name', '')}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
```

## Supported Field Types

| Type | HTML Input | Data Format |
|------|-----------|-------------|
| `text` | Text input | `str` |
| `email` | Email input | `str` |
| `tel` | Phone input | `str` |
| `date` | Date picker | `str` |
| `textarea` | Multi-line text | `str` |
| `longtext` | Large text area | `str` (may contain newlines) |
| `select` | Dropdown | `str` |
| `radio` | Radio buttons | `str` |
| `checkbox` | Checkboxes | `str` (comma-separated) |
| `list` | Dynamic list | `str` (newline-separated) |

## Testing Templates

Templates are standalone Python scripts — test them without a browser:

```bash
pip install python-docx
python -c "
import json, importlib.util
spec = importlib.util.spec_from_file_location('t', 'templates/onboarding.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
result = mod.generate_docx({'first_name': 'Jane', 'last_name': 'Doe', 'email': 'jane@co.com', 'start_date': '2026-04-01'})
print(f'Generated {len(result)} bytes')
"
```

## License

[MIT](LICENSE)
