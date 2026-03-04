# Field Types Reference

Every field in a schema has a `type` that controls how it renders in the form and how its value is passed to the template.

## Quick Reference

| Type | Renders As | Data Format | Needs `options`? |
|------|-----------|-------------|-----------------|
| `text` | Single-line text input | `"Jane"` | no |
| `email` | Email input with browser validation | `"jane@co.com"` | no |
| `tel` | Phone number input | `"(555) 123-4567"` | no |
| `date` | Native date picker | `"2025-03-15"` | no |
| `textarea` | Multi-line text (3 rows) | `"Some notes..."` | no |
| `longtext` | Large textarea with character counter | `"Para 1\nPara 2"` | no |
| `select` | Dropdown menu | `"Engineering"` | yes |
| `radio` | Radio button group | `"Full-Time"` | yes |
| `checkbox` | Checkbox group (multi-select) | `"A, B, C"` | yes |
| `list` | Dynamic add/remove rows with bulk paste | `"X\nY\nZ"` | no |

## Layout Rules

Fields are automatically arranged in the form:

- `text`, `email`, `tel`, `date`, `select` — paired into **two-column rows** when consecutive
- `textarea`, `longtext`, `list`, `radio`, `checkbox` — always **full-width**, breaks any pairing

You control layout through field ordering. Two consecutive `text` fields pair up. A `text` followed by a `longtext` will not.

---

## text

Standard single-line input. Use for names, titles, short answers.

```json
{ "id": "first_name", "label": "First Name", "type": "text", "required": true, "placeholder": "Jane" }
```

**Template:** `data.get('first_name', '')`  → `"Jane"`

## email

Same as `text` but with browser-level email format validation.

```json
{ "id": "email", "label": "Email Address", "type": "email", "required": true, "placeholder": "jane@company.com" }
```

**Template:** `data.get('email', '')` → `"jane@company.com"`

## tel

Phone number input. No format enforcement — accepts any string.

```json
{ "id": "phone", "label": "Phone", "type": "tel", "placeholder": "(555) 123-4567" }
```

**Template:** `data.get('phone', '')` → `"(555) 123-4567"`

## date

Native browser date picker. Value is always in `YYYY-MM-DD` format.

```json
{ "id": "start_date", "label": "Start Date", "type": "date", "required": true }
```

**Template:** `data.get('start_date', '')` → `"2025-03-15"`

To reformat in your template:

```python
from datetime import datetime
raw = data.get('start_date', '')
if raw:
    formatted = datetime.strptime(raw, '%Y-%m-%d').strftime('%B %d, %Y')
    # "March 15, 2025"
```

## textarea

Multi-line text input, 3 rows tall. Good for short notes or comments.

```json
{ "id": "notes", "label": "Notes", "type": "textarea", "placeholder": "Any additional info..." }
```

**Template:** `data.get('notes', '')` → `"Some notes here"`

## longtext

Large text area (6 rows) with a live character counter. Use for bios, descriptions, or any extended prose. Supports `maxLength` to show a limit.

```json
{
  "id": "bio",
  "label": "Professional Bio",
  "type": "longtext",
  "placeholder": "Write a brief biography...",
  "hint": "This appears as a full paragraph in the document",
  "maxLength": 2000
}
```

**Template:** Value may contain `\n` for paragraph breaks.

```python
bio = data.get('bio', '')
for paragraph in bio.split('\n'):
    if paragraph.strip():
        doc.add_paragraph(paragraph.strip())
```

## select

Dropdown menu. Requires an `options` array.

```json
{
  "id": "department",
  "label": "Department",
  "type": "select",
  "required": true,
  "options": ["", "Engineering", "Design", "Marketing", "Sales"]
}
```

Include `""` as the first option — it renders as "— Select —" and serves as the unselected default. The empty string fails validation if `required` is `true`, which prevents submitting without choosing.

**Template:** `data.get('department', '')` → `"Engineering"`

## radio

Single-choice radio button group. Requires an `options` array. Do not include an empty string.

```json
{
  "id": "employment_type",
  "label": "Employment Type",
  "type": "radio",
  "required": true,
  "options": ["Full-Time", "Part-Time", "Contract", "Intern"]
}
```

**Template:** `data.get('employment_type', '')` → `"Full-Time"`

## checkbox

Multi-select checkbox group. Requires an `options` array. Users can select zero or more items.

```json
{
  "id": "equipment_needs",
  "label": "Additional Equipment",
  "type": "checkbox",
  "options": ["Monitor", "Keyboard", "Mouse", "Standing Desk", "Webcam"],
  "hint": "Select all that apply"
}
```

**Template:** Value is a comma-separated string of selected items.

```python
equipment = data.get('equipment_needs', '')  # "Monitor, Keyboard, Webcam"
if equipment:
    items = [e.strip() for e in equipment.split(',') if e.strip()]
```

## list

Dynamic list entry with two input modes:

- **Individual rows** — click "Add item" or press Enter to add rows. Backspace on an empty row removes it. Each row has an × delete button.
- **Bulk paste** — a textarea where users can paste multiple items separated by newlines, which auto-convert to individual rows.

```json
{
  "id": "skills",
  "label": "Key Skills",
  "type": "list",
  "placeholder": "e.g. Python",
  "hint": "Add skills one at a time or paste multiple"
}
```

**Template:** Value is a newline-separated string.

```python
skills = data.get('skills', '')  # "Python\nJavaScript\nRust"
if skills:
    for item in skills.split('\n'):
        if item.strip():
            doc.add_paragraph(item.strip(), style='List Bullet')
```

---

## Choosing the Right Type

| If you need... | Use |
|---------------|-----|
| A short answer (name, title, ID) | `text` |
| An email address | `email` |
| A phone number | `tel` |
| A calendar date | `date` |
| A brief comment (1-3 lines) | `textarea` |
| Extended writing (bio, description) | `longtext` |
| One choice from a fixed list | `select` (5+ options) or `radio` (2-4 options) |
| Multiple choices from a fixed list | `checkbox` |
| A user-defined list of items | `list` |
