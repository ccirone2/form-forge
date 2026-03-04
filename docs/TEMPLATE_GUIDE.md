# Template Guide

A template is a Python script that generates a DOCX file from form data. It runs entirely in the browser via Pyodide — no server required.

## File Location

Place template files in the `templates/` directory of your repo:

```
templates/
├── onboarding.py
├── expense-report.py
└── incident-report.py
```

Each schema references its template via the `template` field (e.g. `"template": "templates/onboarding.py"`). If omitted, FormForge looks for `templates/{schema-filename}.py`.

## Required Interface

Every template must define a `generate_docx` function with this signature:

```python
def generate_docx(data):
    """
    Args:
        data: dict mapping field IDs to string values.

    Returns:
        bytes: The generated .docx file contents.
    """
```

The function receives a flat dictionary where keys are field `id` values from the schema and values are always strings. It must return the raw bytes of a valid `.docx` file.

## Minimal Template

```python
import io
from docx import Document

def generate_docx(data):
    doc = Document()
    doc.add_heading('My Document', level=0)
    doc.add_paragraph(f"Name: {data.get('name', '')}")

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()
```

## Understanding the Data Dictionary

All values in `data` are strings, regardless of field type. Here's how each type is serialized:

| Field Type | Value Format | Example |
|------------|-------------|---------|
| `text`, `email`, `tel` | Plain string | `"Jane Doe"` |
| `date` | ISO format string | `"2025-03-15"` |
| `select` | Selected option string | `"Engineering"` |
| `radio` | Selected option string | `"Full-Time"` |
| `textarea` | Plain string | `"Some notes here"` |
| `longtext` | String with `\n` paragraph breaks | `"First paragraph.\nSecond paragraph."` |
| `checkbox` | Comma-separated string | `"GitHub, Jira, Figma"` |
| `list` | Newline-separated string | `"Python\nJavaScript\nRust"` |

Empty or unfilled fields will be empty strings `""`.

## Parsing Field Types

### Simple fields (text, email, tel, date, select, radio, textarea)

Use directly:

```python
name = data.get('first_name', '')
department = data.get('department', '')
```

### Long text → paragraphs

```python
bio = data.get('bio', '')
if bio:
    doc.add_heading('Bio', level=1)
    for paragraph in bio.split('\n'):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())
```

### List → bullet points

```python
skills = data.get('skills', '')
if skills:
    doc.add_heading('Skills', level=1)
    for item in skills.split('\n'):
        if item.strip():
            doc.add_paragraph(item.strip(), style='List Bullet')
```

### Checkbox → comma-separated items

```python
tools = data.get('tools_used', '')
if tools:
    tool_list = [t.strip() for t in tools.split(',') if t.strip()]
    doc.add_paragraph(f"Tools: {', '.join(tool_list)}")
```

## Common python-docx Patterns

### Styled document with title

```python
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

title = doc.add_heading('Document Title', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

### Key-value table

```python
from docx.enum.table import WD_TABLE_ALIGNMENT

table = doc.add_table(rows=0, cols=2)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

rows = [
    ('Name', data.get('name', '')),
    ('Date', data.get('date', '')),
    ('Department', data.get('department', '')),
]

for label, value in rows:
    row = table.add_row()
    row.cells[0].paragraphs[0].add_run(label).bold = True
    row.cells[1].paragraphs[0].add_run(value or '\u2014')
```

### Signature block

```python
doc.add_paragraph('')
doc.add_heading('Signatures', level=1)

sig_table = doc.add_table(rows=1, cols=2)
for i, label in enumerate(['Employee Signature', 'Date']):
    cell = sig_table.rows[0].cells[i]
    p = cell.paragraphs[0]
    p.add_run('\n\n')
    p.add_run('_' * 35 + '\n')
    run = p.add_run(label)
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
```

### Page break

```python
doc.add_page_break()
```

### Centered footer text

```python
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Auto-generated document.')
run.font.size = Pt(8)
run.italic = True
run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
```

## Available Libraries

These are available in the Pyodide runtime:

| Library | Import | Purpose |
|---------|--------|---------|
| python-docx | `from docx import Document` | DOCX generation |
| Python stdlib | `io`, `json`, `datetime`, `re`, `math`, etc. | General utilities |

Additional pure-Python packages can be installed via `micropip` if needed. Packages with C extensions (numpy, pandas, etc.) will only work if they have pre-built Pyodide wheels — check the [Pyodide packages list](https://pyodide.org/en/stable/usage/packages-in-pyodide.html).

## Helper Function Pattern

For consistency across templates, extract common operations into helper functions at the top of your file:

```python
from docx.shared import Pt, RGBColor

MUTED = RGBColor(0x99, 0x99, 0x99)

def add_table_section(doc, heading, rows):
    """Add a heading followed by a key-value table."""
    doc.add_heading(heading, level=1)
    table = doc.add_table(rows=0, cols=2)
    table.style = 'Light Grid Accent 1'
    for label, value in rows:
        row = table.add_row()
        row.cells[0].paragraphs[0].add_run(label).bold = True
        row.cells[1].paragraphs[0].add_run(value or '\u2014')
    doc.add_paragraph('')

def add_bullet_list(doc, heading, items_str):
    """Add a heading followed by bullet points from a newline-separated string."""
    doc.add_heading(heading, level=2)
    if items_str and items_str.strip():
        for item in items_str.split('\n'):
            if item.strip():
                doc.add_paragraph(item.strip(), style='List Bullet')
    else:
        p = doc.add_paragraph()
        r = p.add_run('No items listed.')
        r.italic = True
        r.font.color.rgb = MUTED
    doc.add_paragraph('')
```

Then your `generate_docx` function stays clean:

```python
def generate_docx(data):
    doc = Document()
    doc.add_heading('My Report', level=0)

    add_table_section(doc, 'Details', [
        ('Name', data.get('name', '')),
        ('Date', data.get('date', '')),
    ])
    add_bullet_list(doc, 'Action Items', data.get('actions', ''))

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()
```

## Testing Locally

You can test templates without a browser using standard Python:

```bash
pip install python-docx
python -c "
import json
from my_template import generate_docx

data = {'name': 'Test User', 'date': '2025-01-15', 'department': 'Engineering'}
result = generate_docx(data)

with open('test_output.docx', 'wb') as f:
    f.write(result)
print(f'Generated {len(result)} bytes')
"
```

Or use FormForge's Local Files feature to drop in your `.json` and `.py` and test interactively.

## Tips

- Always use `data.get('field_id', '')` with a default — never assume a key exists
- Handle empty strings gracefully in your document (show "—" or "Not provided" instead of blank space)
- Keep templates self-contained — all imports and helpers in one file
- Use `doc.add_paragraph('')` for vertical spacing between sections
- Test with both fully filled and mostly empty form data to make sure the document looks good either way
